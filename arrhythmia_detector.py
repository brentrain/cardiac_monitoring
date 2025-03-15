import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout
from biosppy.signals import ecg

class ArrhythmiaDetector:
    def __init__(self):
        self.model = self._build_model()
        
    def _build_model(self):
        model = Sequential([
            LSTM(64, input_shape=(100, 1), return_sequences=True),
            Dropout(0.2),
            LSTM(32),
            Dense(32, activation='relu'),
            Dense(16, activation='relu'),
            Dense(4, activation='softmax')  # 4 classes: Normal, AFib, VTach, Heart Block
        ])
        model.compile(optimizer='adam',
                     loss='categorical_crossentropy',
                     metrics=['accuracy'])
        return model
    
    def preprocess_signal(self, ecg_signal):
        """Preprocess ECG signal using biosppy"""
        try:
            # Process ECG signal
            out = ecg.ecg(signal=ecg_signal, sampling_rate=250., show=False)
            # Extract features
            cleaned = out['filtered']
            r_peaks = out['rpeaks']
            templates = out['templates']
            
            # Calculate heart rate variability
            rr_intervals = np.diff(r_peaks)
            
            return {
                'cleaned_signal': cleaned,
                'r_peaks': r_peaks,
                'templates': templates,
                'rr_intervals': rr_intervals
            }
        except Exception as e:
            print(f"Error preprocessing signal: {str(e)}")
            return None

    def detect_arrhythmia(self, ecg_signal):
        """
        Detect arrhythmia in ECG signal
        Returns: Dictionary with arrhythmia type and confidence score
        """
        processed = self.preprocess_signal(ecg_signal)
        if processed is None:
            return {'error': 'Failed to process ECG signal'}
        
        # Extract features for prediction
        # In real implementation, you would use the processed signal
        # to extract relevant features for your trained model
        
        # Simulate prediction for demonstration
        # In reality, you would:
        # 1. Load a pre-trained model
        # 2. Use real ECG data
        # 3. Make actual predictions
        
        # Example prediction (simulated)
        prediction = {
            'rhythm_type': self._classify_rhythm(processed),
            'confidence': np.random.uniform(0.8, 0.99),
            'is_lethal': self._is_lethal_arrhythmia(processed)
        }
        
        return prediction
    
    def _classify_rhythm(self, processed_signal):
        """
        Classify the heart rhythm based on processed signal
        This is a simplified version - in reality, you would use your trained model
        """
        # Example classification logic
        rr_intervals = processed_signal['rr_intervals']
        
        if np.std(rr_intervals) > 50:
            return 'Atrial Fibrillation'
        elif np.mean(rr_intervals) < 400:
            return 'Ventricular Tachycardia'
        elif np.std(rr_intervals) < 10:
            return 'Heart Block'
        else:
            return 'Normal Sinus Rhythm'
    
    def _is_lethal_arrhythmia(self, processed_signal):
        """
        Determine if the arrhythmia is potentially lethal
        """
        rhythm_type = self._classify_rhythm(processed_signal)
        lethal_rhythms = ['Ventricular Tachycardia', 'Ventricular Fibrillation']
        return rhythm_type in lethal_rhythms 