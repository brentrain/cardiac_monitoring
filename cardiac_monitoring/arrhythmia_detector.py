import numpy as np

class ArrhythmiaDetector:
    def __init__(self):
        self.normal_hr_range = (60, 100)  # Normal heart rate range in BPM
        
    def detect_arrythmia(self, ecg_data, sampling_rate=250):
        """
        Simple rule-based arrhythmia detection based on heart rate and RR intervals.
        
        Args:
            ecg_data (numpy.ndarray): ECG signal data
            sampling_rate (int): Sampling rate in Hz
            
        Returns:
            dict: Dictionary containing arrhythmia detection results
        """
        # Calculate heart rate from RR intervals
        rr_intervals = self._calculate_rr_intervals(ecg_data, sampling_rate)
        if not rr_intervals:
            return {
                'has_arrythmia': False,
                'confidence': 0.0,
                'type': 'Unknown',
                'rhythm': 'Unknown',
                'details': 'Insufficient data for analysis'
            }
            
        heart_rate = 60 / (np.mean(rr_intervals) / sampling_rate)
        rr_std = np.std(rr_intervals)
        
        # Simple rule-based detection
        has_arrythmia = False
        arrhythmia_type = 'Normal'
        rhythm = 'Normal Sinus Rhythm'
        confidence = 0.0
        
        if heart_rate < self.normal_hr_range[0]:
            has_arrythmia = True
            arrhythmia_type = 'Bradycardia'
            rhythm = 'Sinus Bradycardia'
            confidence = min(1.0, (self.normal_hr_range[0] - heart_rate) / 20)
        elif heart_rate > self.normal_hr_range[1]:
            has_arrythmia = True
            arrhythmia_type = 'Tachycardia'
            rhythm = 'Sinus Tachycardia'
            confidence = min(1.0, (heart_rate - self.normal_hr_range[1]) / 40)
        elif rr_std > 0.2:  # High variability in RR intervals
            has_arrythmia = True
            arrhythmia_type = 'Irregular Rhythm'
            rhythm = 'Irregular Rhythm'
            confidence = min(1.0, rr_std)
            
        # Check for lethal rhythms
        if self._is_ventricular_fibrillation(ecg_data):
            has_arrythmia = True
            arrhythmia_type = 'Ventricular Fibrillation'
            rhythm = 'Ventricular Fibrillation'
            confidence = 1.0
        elif self._is_ventricular_tachycardia(ecg_data, heart_rate):
            has_arrythmia = True
            arrhythmia_type = 'Ventricular Tachycardia'
            rhythm = 'Ventricular Tachycardia'
            confidence = 1.0
        elif self._is_torsades_de_pointes(ecg_data):
            has_arrythmia = True
            arrhythmia_type = 'Torsades de Pointes'
            rhythm = 'Torsades de Pointes'
            confidence = 1.0
        elif self._is_asystole(ecg_data):
            has_arrythmia = True
            arrhythmia_type = 'Asystole'
            rhythm = 'Asystole'
            confidence = 1.0
            
        return {
            'has_arrythmia': has_arrythmia,
            'confidence': float(confidence),
            'type': arrhythmia_type,
            'rhythm': rhythm,
            'details': f'Heart Rate: {heart_rate:.1f} BPM, RR Variability: {rr_std:.3f}'
        }
        
    def _calculate_rr_intervals(self, ecg_data, sampling_rate):
        """
        Calculate RR intervals from ECG data using simple peak detection.
        
        Args:
            ecg_data (numpy.ndarray): ECG signal data
            sampling_rate (int): Sampling rate in Hz
            
        Returns:
            list: List of RR intervals in samples
        """
        # Simple peak detection
        peaks = []
        window_size = int(0.2 * sampling_rate)  # 200ms window
        
        for i in range(window_size, len(ecg_data) - window_size):
            if ecg_data[i] == max(ecg_data[i-window_size:i+window_size]):
                peaks.append(i)
                
        if len(peaks) < 2:
            return []
            
        # Calculate RR intervals
        rr_intervals = np.diff(peaks)
        return rr_intervals.tolist()
        
    def _is_ventricular_fibrillation(self, ecg_data):
        """Simple check for ventricular fibrillation based on signal variability"""
        return np.std(ecg_data) > 2.0  # High variability in signal
        
    def _is_ventricular_tachycardia(self, ecg_data, heart_rate):
        """Check for ventricular tachycardia based on heart rate"""
        return heart_rate > 150  # Very high heart rate
        
    def _is_torsades_de_pointes(self, ecg_data):
        """Check for Torsades de Pointes based on signal pattern"""
        # Look for characteristic twisting pattern around baseline
        signal_mean = np.mean(ecg_data)
        crossings = np.sum(np.diff(np.signbit(ecg_data - signal_mean)))
        return crossings > 10  # Multiple baseline crossings indicate twisting pattern
        
    def _is_asystole(self, ecg_data):
        """Check for asystole based on signal amplitude"""
        return np.max(np.abs(ecg_data)) < 0.1  # Very low signal amplitude 