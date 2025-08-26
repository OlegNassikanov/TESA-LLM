import ctypes
import json
import binascii
from collections import defaultdict
from fuzzywuzzy import fuzz

class TESACompressor:
    def __init__(self, max_markers=16384):
        self.max_markers = max_markers
        self.dictionary = {}
        self.reverse_dict = {}
        self.temp_dict = {}
        self.next_id = 1
        self.next_temp_id = 1
        self.frequency = defaultdict(int)
        self.lib = ctypes.CDLL('./tesa_packer.so')
        self.lib.pack_markers.argtypes = [ctypes.c_uint16, ctypes.c_uint16]
        self.lib.pack_markers.restype = ctypes.c_uint32

    def add_to_dictionary(self, phrase):
        self.frequency[phrase] += 1
        if phrase not in self.reverse_dict:
            for known_phrase, marker in self.reverse_dict.items():
                if fuzz.ratio(phrase.lower(), known_phrase.lower()) > 90:
                    return marker
            if self.next_id < self.max_markers:
                marker = f'S{self.next_id}'
                self.dictionary[marker] = phrase
                self.reverse_dict[phrase] = marker
                self.next_id += 1
            else:
                marker = f'T{self.next_temp_id}'
                self.temp_dict[marker] = phrase
                self.next_temp_id += 1
            return marker
        return self.reverse_dict[phrase]

    def compress(self, text):
        words = text.split()
        compressed = []
        i = 0
        while i < len(words):
            if i + 1 < len(words):
                pair = f'{words[i]} {words[i+1]}'
                if self.frequency[pair] > 2:
                    compressed.append(self.add_to_dictionary(pair))
                    i += 2
                    continue
            compressed.append(self.add_to_dictionary(words[i]))
            i += 1
        delta_compressed = []
        for c in compressed:
            if c.startswith('S'):
                delta_compressed.append(int(c[1:]) << 2)
            elif c.startswith('T'):
                delta_compressed.append((int(c[1:]) << 2) | 0b01)
            else:
                delta_compressed.append(c)
        if len(delta_compressed) > 1:
            delta_compressed = [delta_compressed[0]] + [
                delta_compressed[i] - delta_compressed[i - 1] for i in range(1, len(delta_compressed))
            ]
        return delta_compressed

    def decompress(self, compressed):
        restored = [compressed[0]]
        for delta in compressed[1:]:
            restored.append(restored[-1] + delta)
        result = []
        for r in restored:
            if isinstance(r, str):
                result.append(r)
            else:
                marker_type = r & 0b11
                marker_id = r >> 2
                if marker_type == 0b01:
                    result.append(self.temp_dict.get(f'T{marker_id}', f'T{marker_id}'))
                else:
                    result.append(self.dictionary.get(f'S{marker_id}', f'S{marker_id}'))
        return ' '.join(result)

    def pack_markers(self, marker1, marker2):
        m1 = int(marker1[1:]) if marker1.startswith('S') else 0
        m2 = int(marker2[1:]) if marker2.startswith('S') else 0
        return self.lib.pack_markers(m1, m2)

    def to_json(self, compressed):
        return json.dumps(compressed)

    def to_binary(self, compressed):
        version = 1
        count = len(compressed)
        data = bytearray([version, count])
        for c in compressed:
            if isinstance(c, int):
                data.extend((c >> 8).to_bytes(1, 'big'))
                data.extend((c & 0xFF).to_bytes(1, 'big'))
        crc = binascii.crc_hqx(data, 0)
        data.extend(crc.to_bytes(2, 'big'))
        return data


# 🧠 Motif Logic: Instruction-as-Music
def execute(action, duration=0.5):
    print(f"Executing: {action} for {duration} seconds")


def interpret_motif(motif):
    for step in motif:
        execute(step.get('action', 'noop'), step.get('duration', 0.5))


# 🎵 Example usage
note = {
    'pitch': 'C4',
    'duration': 0.5,
    'velocity': 0.8,
    'action': 'send_ping'
}

note2 = {
    'pitch': 'E4',
    'duration': 0.25,
    'velocity': 0.9,
    'action': 'check_status'
}

note3 = {
    'pitch': 'G4',
    'duration': 0.75,
    'velocity': 0.7,
    'action': 'confirm_env'
}

motif = [note, note2, note3]

if __name__ == '__main__':
    interpret_motif(motif)
