import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QTextEdit, QVBoxLayout, QFileDialog, QLabel, QProgressBar
)
import whisper

def remove_ads(transcription_result):
    """Filter out ad-related segments from transcription."""
    ad_keywords = [
        "sponsored by", "brought to you by", "thanks to our sponsor",
        "use promo code", "limited-time offer", "our partnership with"
    ]
    
    filtered_segments = []
    
    for segment in transcription_result["segments"]:
        segment_text = segment["text"].lower()
        if not any(keyword in segment_text for keyword in ad_keywords):
            filtered_segments.append(segment_text)

    return " ".join(filtered_segments)

class TranscriptionApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.model = whisper.load_model("tiny")  # Use "tiny" for faster processing
        self.transcription_active = False

    def initUI(self):
        self.setWindowTitle("MP3 Transcription App")
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        self.label = QLabel("Select an MP3 file to transcribe")
        layout.addWidget(self.label)

        self.select_button = QPushButton("Select File")
        self.select_button.clicked.connect(self.openFileDialog)
        layout.addWidget(self.select_button)

        self.transcribe_button = QPushButton("Transcribe")
        self.transcribe_button.clicked.connect(self.transcribeAudio)
        self.transcribe_button.setEnabled(False)
        layout.addWidget(self.transcribe_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancelTranscription)
        self.cancel_button.setEnabled(False)
        layout.addWidget(self.cancel_button)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress bar
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        layout.addWidget(self.text_area)

        self.save_button = QPushButton("Save Transcript")
        self.save_button.clicked.connect(self.saveTranscript)
        self.save_button.setEnabled(False)
        layout.addWidget(self.save_button)
        self.setLayout(layout)
        self.audio_file = None

    def openFileDialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Audio File", "", "Audio Files (*.mp3 *.wav)")
        if file_path:
            self.audio_file = file_path
            self.label.setText(f"✅ Selected: {os.path.basename(file_path)}")
            self.transcribe_button.setEnabled(True)

    def transcribeAudio(self):
        if not self.audio_file:
            return

        self.transcription_active = True
        self.label.setText("Transcribing... Please wait.")
        self.progress_bar.setVisible(True)  # Show progress bar
        self.cancel_button.setEnabled(True)
        QApplication.processEvents()  # Update UI while transcribing

        result = self.model.transcribe(self.audio_file, word_timestamps=True)
        if self.transcription_active:
            clean_transcript = remove_ads(result)
            self.text_area.setPlainText(clean_transcript)
            self.save_button.setEnabled(True)
            self.label.setText("✅ Transcription Complete!")
        else:
            self.label.setText("❌ Transcription Canceled!")
        
        self.progress_bar.setVisible(False)  # Hide progress bar
        self.cancel_button.setEnabled(False)
        self.transcription_active = False

    def cancelTranscription(self):
        self.transcription_active = False
        self.label.setText("❌ Canceling transcription...")
        QApplication.processEvents()

    def saveTranscript(self):
        if not self.text_area.toPlainText():
            return

        save_path, _ = QFileDialog.getSaveFileName(self, "Save Transcript", "", "Text Files (*.txt)")
        if save_path:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(self.text_area.toPlainText())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TranscriptionApp()
    window.show()
    sys.exit(app.exec())
