"""Modulos de pre-processamento do projeto epilepsy-detection."""

try:
    from .edf_reader import load_edf, STANDARD_CHANNELS
except ModuleNotFoundError:
    load_edf = None
    STANDARD_CHANNELS = []

from .seizure_parser import parse_seizure_list
from .segmentor import extract_segments

try:
    from .stft_converter import segment_to_spectrogram, save_spectrogram
except ModuleNotFoundError:
    segment_to_spectrogram = None
    save_spectrogram = None

from .image_enhancer import (
    apply_histogram_equalization,
    apply_clahe,
    apply_brightness,
    apply_contrast,
    enhance_spectrogram,
)
from .conv_filters import (
    KERNEL_SMOOTHING,
    KERNEL_EDGE_DETECTION,
    KERNEL_SOBEL,
    convolve2d_manual,
    apply_smoothing_filter,
    apply_edge_detector_filter,
    apply_sobel_filter,
)
