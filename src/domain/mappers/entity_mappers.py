"""Mapper classes for converting between domain entities and DTOs."""
from typing import List

from ..dtos.content_dtos import PageContentDTO, TextBlockDTO, TableDTO
from ..dtos.coordinates_dto import CoordinatesDTO
from ..dtos.document_dtos import DocumentMetadataDTO, DocumentOutputDTO
from ..entities.document import Document
from ..value_objects.page import Page
from ..value_objects.text_block import TextBlock
from ..value_objects.table import Table
from ..value_objects.text_coordinates import TextCoordinates
from ..value_objects.document_metadata import DocumentMetadata

class DocumentMapper:
    """Mapper class for Document related conversions."""

    @staticmethod
    def to_dto(document: Document) -> DocumentOutputDTO:
        """Convert Document entity to DocumentOutputDTO."""
        return DocumentOutputDTO(
            id=document.id,
            file_path=document.path,
            total_pages=document.total_pages,
            processed_successfully=document.processed,
            error_message=document.error,
            creation_date=document.metadata.creation_date if document.metadata else None,
            author=document.metadata.author if document.metadata else None
        )

    @staticmethod
    def metadata_to_dto(metadata: DocumentMetadata) -> DocumentMetadataDTO:
        """Convert DocumentMetadata value object to DTO."""
        return DocumentMetadataDTO(
            title=metadata.title,
            author=metadata.author,
            creation_date=metadata.creation_date,
            modification_date=metadata.modification_date,
            producer=metadata.producer,
            page_count=metadata.page_count
        )

class PageMapper:
    """Mapper class for Page related conversions."""

    @staticmethod
    def to_dto(page: Page) -> PageContentDTO:
        """Convert Page value object to PageContentDTO."""
        return PageContentDTO(
            page_number=page.number,
            text_blocks=[TextBlockMapper.to_dto(block) for block in page.text_blocks],
            tables=[TableMapper.to_dto(table) for table in page.tables],
            rotation=page.rotation,
            is_scanned=page.has_scanned_content,
            confidence_score=page.confidence_score
        )

    @staticmethod
    def from_dto(dto: PageContentDTO) -> Page:
        """Convert PageContentDTO to Page value object."""
        return Page(
            number=dto.page_number,
            text_blocks=[TextBlockMapper.from_dto(block) for block in dto.text_blocks],
            tables=[TableMapper.from_dto(table) for table in dto.tables],
            rotation=dto.rotation,
            has_scanned_content=dto.is_scanned,
            confidence_score=dto.confidence_score
        )

class TextBlockMapper:
    """Mapper class for TextBlock related conversions."""

    @staticmethod
    def to_dto(block: TextBlock) -> TextBlockDTO:
        """Convert TextBlock value object to TextBlockDTO."""
        return TextBlockDTO(
            content=block.content,
            coordinates=CoordinatesMapper.to_dto(block.coordinates),
            confidence_score=block.confidence_score,
            language=block.language
        )

    @staticmethod
    def from_dto(dto: TextBlockDTO) -> TextBlock:
        """Convert TextBlockDTO to TextBlock value object."""
        return TextBlock(
            content=dto.content,
            coordinates=CoordinatesMapper.from_dto(dto.coordinates),
            confidence_score=dto.confidence_score,
            language=dto.language
        )

class TableMapper:
    """Mapper class for Table related conversions."""

    @staticmethod
    def to_dto(table: Table) -> TableDTO:
        """Convert Table value object to TableDTO."""
        return TableDTO(
            data=table.data,
            coordinates=CoordinatesMapper.to_dto(table.coordinates),
            confidence_score=table.confidence_score
        )

    @staticmethod
    def from_dto(dto: TableDTO) -> Table:
        """Convert TableDTO to Table value object."""
        return Table(
            data=dto.data,
            coordinates=CoordinatesMapper.from_dto(dto.coordinates),
            confidence_score=dto.confidence_score
        )

class CoordinatesMapper:
    """Mapper class for TextCoordinates related conversions."""

    @staticmethod
    def to_dto(coordinates: TextCoordinates) -> CoordinatesDTO:
        """Convert TextCoordinates value object to CoordinatesDTO."""
        return CoordinatesDTO(
            x1=coordinates.x1,
            y1=coordinates.y1,
            x2=coordinates.x2,
            y2=coordinates.y2,
            page_number=0  # This should be set by the caller
        )

    @staticmethod
    def from_dto(dto: CoordinatesDTO) -> TextCoordinates:
        """Convert CoordinatesDTO to TextCoordinates value object."""
        return TextCoordinates(
            x1=dto.x1,
            y1=dto.y1,
            x2=dto.x2,
            y2=dto.y2
        )
