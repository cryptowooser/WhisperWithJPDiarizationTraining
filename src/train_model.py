import os
import pytorch_lightning as pl
from pyannote.database import get_protocol, FileFinder, Protocol
from pyannote.audio import Pipeline, Model
from pyannote.audio.tasks import Segmentation
from types import MethodType
from torch.optim import Adam
from pytorch_lightning.callbacks import EarlyStopping, ModelCheckpoint, RichProgressBar
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def train_diarization_model(
    protocol_name,
    hf_token,
    pretrained_pipeline_name="pyannote/speaker-diarization-3.1",
    pretrained_model_name="pyannote/segmentation-3.0",
    batch_size=128,
    num_workers=0,
    learning_rate=1e-4,
    early_stopping_patience=10,
    max_epochs=300
):
    # Set up environment
    os.environ["PYANNOTE_DATABASE_CONFIG"] = "database.yml"
    logger.info(f"PYANNOTE_DATABASE_CONFIG set to: {os.environ['PYANNOTE_DATABASE_CONFIG']}")

    # Load dataset
    try:
        dataset = get_protocol(protocol_name, {"audio": FileFinder()})
        logger.info(f"Successfully loaded protocol: {protocol_name}")
        if not isinstance(dataset, Protocol):
            raise ValueError(f"Expected Protocol object, got {type(dataset)}")
    except Exception as e:
        logger.error(f"Failed to load protocol: {protocol_name}")
        logger.error(f"Error: {str(e)}")
        raise

    # Load pretrained pipeline and model
    pretrained_pipeline = Pipeline.from_pretrained(pretrained_pipeline_name, use_auth_token=hf_token)
    model = Model.from_pretrained(pretrained_model_name, use_auth_token=hf_token)

    # Set up task
    task = Segmentation(
        dataset,
        duration=model.specifications.duration,
        max_num_speakers=len(model.specifications.classes),
        batch_size=batch_size,
        num_workers=num_workers,
        loss="bce",
        vad_loss="bce"
    )
    model.task = task
    
    # Initialize the task
    logger.info("Setting up the task...")
    task.prepare_data()
    task.setup()
    logger.info("Task setup complete.")

    # Configure optimizer
    def configure_optimizers(self):
        return Adam(self.parameters(), lr=learning_rate)

    model.configure_optimizers = MethodType(configure_optimizers, model)

    # Set up callbacks
    monitor, direction = task.val_monitor
    checkpoint = ModelCheckpoint(
        monitor=monitor,
        mode=direction,
        save_top_k=1,
        every_n_epochs=1,
        save_last=False,
        save_weights_only=False,
        filename="{epoch}",
        verbose=False,
    )
    early_stopping = EarlyStopping(
        monitor=monitor,
        mode=direction,
        min_delta=0.0,
        patience=early_stopping_patience,
        strict=True,
        verbose=False,
    )
    callbacks = [RichProgressBar(), checkpoint, early_stopping]

    # Train the model
    trainer = pl.Trainer(
        callbacks=callbacks,
        accelerator="gpu",
        max_epochs=max_epochs   
    )
    trainer.fit(model)

    print(task.val_monitor)
    print(f"Model path: {trainer.checkpoint_callback.best_model_path}")

    return model, trainer

# Example usage:
if __name__ == "__main__":
    trained_model, trainer = train_diarization_model(
        protocol_name="anime_finetune.SpeakerDiarization.full",
        hf_token=os.environ.get('HF_TOKEN_NOT_LOGIN'),
    )
