import psutil
from fastapi import WebSocket
from pdf2image import convert_from_path

from app.core.config import settings
from app.core.logging import logger
from app.services.ocr import process_image
from app.services.ai import process_chunk
from app.utils.text import split_into_chunks
from app.utils.time import estimate_processing_time, estimate_remaining_time

async def process_pdf(pdf_path: str, websocket: WebSocket) -> str:
    """
    Process a PDF file and generate a summary.
    """
    try:
        # Convert PDF to images
        await websocket.send_json({
            'status': 'converting',
            'message': 'Converting PDF to images...'
        })
        
        images = convert_from_path(pdf_path)
        total_pages = len(images)
        
        await websocket.send_json({
            'status': 'processing',
            'total_pages': total_pages,
            'current_page': 0
        })

        # Process each page
        all_text = []
        for i, image in enumerate(images, 1):
            # Memory check
            memory = psutil.virtual_memory()
            if memory.percent > settings.MAX_MEMORY_PERCENT:
                await websocket.send_json({
                    'warning': f'High memory usage detected: {memory.percent}%'
                })
                
            # Extract text from image
            text = process_image(image)
            if text:
                all_text.append(text)
                logger.info(f"OCR Text from page {i}/{total_pages} (length: {len(text)} chars):\n{text}")
                
            await websocket.send_json({
                'status': 'processing',
                'current_page': i,
                'total_pages': total_pages,
                'progress': i / total_pages
            })

        # Process text chunks
        combined_text = ' '.join(all_text)
        logger.info(f"Complete OCR Text before chunking (length: {len(combined_text)} chars):\n{combined_text}")
        chunks = split_into_chunks(combined_text)
        total_chunks = len(chunks)
        
        await websocket.send_json({
            'status': 'analyzing',
            'message': 'Analyzing content...',
            'total_chunks': total_chunks,
            'estimated_time': estimate_processing_time(total_chunks)
        })

        # Process chunks with AI
        summaries = []
        running_summary = None
        for i, chunk in enumerate(chunks):
            summary = await process_chunk(
                chunk, 
                websocket, 
                chunk_index=i,
                total_chunks=total_chunks,
                previous_summary=running_summary
            )
            summaries.append(summary)
            # Keep only the most recent summary for context
            running_summary = summary
            
            await websocket.send_json({
                'status': 'analyzing',
                'current_chunk': i + 1,
                'total_chunks': total_chunks,
                'progress': (i + 1) / total_chunks,
                'estimated_remaining': estimate_remaining_time(i + 1, total_chunks)
            })

        # Combine summaries with proper section numbering and formatting
        sections = []
        for i, summary in enumerate(summaries, 1):
            section_header = f"## Section {i}"
            sections.append(f"{section_header}\n\n{summary}")
        
        final_summary = "# Document Summary\n\n" + "\n\n".join(sections)
        logger.info(f"Final Combined Summary:\n{final_summary}")
        return final_summary

    except Exception as e:
        logger.error(f"PDF processing failed: {str(e)}")
        await websocket.send_json({
            'error': f'PDF processing failed: {str(e)}'
        })
        raise 