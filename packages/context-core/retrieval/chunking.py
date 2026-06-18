"""
Recursive Chunker — Splits text into chunks respecting document structure.

Recursively splits by paragraphs, then sentences, then characters.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Chunk:
    """A chunk of text with metadata."""
    content: str
    index: int
    start_char: int
    end_char: int
    metadata: dict = field(default_factory=dict)


class RecursiveChunker:
    """
    Recursive text chunker that respects document structure.

    Splitting priority:
    1. Paragraphs (double newline)
    2. Sentences (period, exclamation, question mark)
    3. Fixed character limit
    """

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        min_chunk_size: int = 100,
    ):
        """
        Initialize recursive chunker.

        Args:
            chunk_size: Maximum chunk size in characters
            chunk_overlap: Overlap between chunks in characters
            min_chunk_size: Minimum chunk size in characters
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size

    def chunk(self, text: str, metadata: Optional[dict] = None) -> list[Chunk]:
        """
        Split text into chunks recursively.

        Args:
            text: Text to split
            metadata: Optional metadata to attach to each chunk

        Returns:
            List of Chunk objects
        """
        if not text or not text.strip():
            return []

        metadata = metadata or {}
        chunks = []
        self._recursive_split(text, 0, metadata, chunks)

        # Apply overlap
        if self.chunk_overlap > 0 and len(chunks) > 1:
            chunks = self._apply_overlap(chunks)

        return chunks

    def _recursive_split(
        self,
        text: str,
        start_offset: int,
        metadata: dict,
        chunks: list[Chunk],
    ):
        """Recursively split text into chunks."""
        text = text.strip()
        if not text:
            return

        # If text fits in one chunk, add it
        if len(text) <= self.chunk_size:
            chunks.append(Chunk(
                content=text,
                index=len(chunks),
                start_char=start_offset,
                end_char=start_offset + len(text),
                metadata=metadata.copy(),
            ))
            return

        # Try splitting by paragraphs first
        paragraphs = re.split(r'\n\s*\n', text)
        if len(paragraphs) > 1:
            current_pos = start_offset
            for para in paragraphs:
                para = para.strip()
                if para:
                    if len(para) <= self.chunk_size:
                        chunks.append(Chunk(
                            content=para,
                            index=len(chunks),
                            start_char=current_pos,
                            end_char=current_pos + len(para),
                            metadata=metadata.copy(),
                        ))
                    else:
                        self._recursive_split(para, current_pos, metadata, chunks)
                current_pos += len(para) + 2  # +2 for \n\n
            return

        # Try splitting by sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        if len(sentences) > 1:
            current_chunk = ""
            current_pos = start_offset

            for sentence in sentences:
                if len(current_chunk) + len(sentence) + 1 <= self.chunk_size:
                    current_chunk += (" " if current_chunk else "") + sentence
                else:
                    if current_chunk:
                        chunks.append(Chunk(
                            content=current_chunk,
                            index=len(chunks),
                            start_char=current_pos,
                            end_char=current_pos + len(current_chunk),
                            metadata=metadata.copy(),
                        ))
                        current_pos += len(current_chunk) + 1
                    current_chunk = sentence

            if current_chunk:
                chunks.append(Chunk(
                    content=current_chunk,
                    index=len(chunks),
                    start_char=current_pos,
                    end_char=current_pos + len(current_chunk),
                    metadata=metadata.copy(),
                ))
            return

        # Last resort: split by characters
        chunk_text = text[:self.chunk_size]
        chunks.append(Chunk(
            content=chunk_text,
            index=len(chunks),
            start_char=start_offset,
            end_char=start_offset + len(chunk_text),
            metadata=metadata.copy(),
        ))

        # Calculate overlap-aware next position
        next_pos = self.chunk_size - self.chunk_overlap
        if next_pos < 1:
            next_pos = self.chunk_size  # Avoid infinite loop

        remaining = text[next_pos:]
        if remaining.strip() and len(remaining) >= self.min_chunk_size:
            self._recursive_split(remaining, start_offset + next_pos, metadata, chunks)

    def _apply_overlap(self, chunks: list[Chunk]) -> list[Chunk]:
        """Apply overlap between consecutive chunks."""
        if len(chunks) <= 1:
            return chunks

        overlapped_chunks = [chunks[0]]

        for i in range(1, len(chunks)):
            prev_content = chunks[i - 1].content
            curr_content = chunks[i].content

            # Get overlap from end of previous chunk
            overlap_text = prev_content[-self.chunk_overlap:] if len(prev_content) > self.chunk_overlap else ""

            # Prepend overlap to current chunk
            new_content = (overlap_text + " " + curr_content).strip()

            overlapped_chunks.append(Chunk(
                content=new_content,
                index=i,
                start_char=chunks[i].start_char,
                end_char=chunks[i].end_char,
                metadata=chunks[i].metadata.copy(),
            ))

        return overlapped_chunks

    def chunk_documents(
        self,
        documents: list[dict],
        content_key: str = "content",
    ) -> list[Chunk]:
        """
        Chunk multiple documents.

        Args:
            documents: List of document dicts with content
            content_key: Key containing the text content

        Returns:
            List of Chunk objects
        """
        all_chunks = []
        for doc in documents:
            content = doc.get(content_key, "")
            metadata = {k: v for k, v in doc.items() if k != content_key}
            chunks = self.chunk(content, metadata)
            all_chunks.extend(chunks)
        return all_chunks