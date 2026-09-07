"""
src/preprocessing
-----------------
Modulos de pre-processamento para o projeto epilepsy-detection.

Modulos:
    edf_reader      : Carregamento e validacao de arquivos EDF.
    seizure_parser  : Leitura das anotacoes Seizures-list-PNxx.txt.
    segmentor       : Extracao de segmentos temporais.
    stft_converter  : Geracao de espectogramas STFT.
"""

from .edf_reader import load_edf, STANDARD_CHANNELS
from .seizure_parser import parse_seizure_list
from .segmentor import extract_segments
from .stft_converter import segment_to_spectrogram, save_spectrogram

__all__ = [
    "load_edf",
    "STANDARD_CHANNELS",
    "parse_seizure_list",
    "extract_segments",
    "segment_to_spectrogram",
    "save_spectrogram",
]
