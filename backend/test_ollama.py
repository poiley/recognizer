import asyncio
import os
import gc
import pytesseract
from pdf2image import convert_from_path
import ollama
from datetime import datetime

async def log(message: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] {message}")

async def process_pdf_test(pdf_path: str) -> str:
    await log(f"Starting PDF processing: {pdf_path}")
    full_text = ''
    
    try:
        await log("Converting PDF to images...")
        images = convert_from_path(
            pdf_path,
            dpi=200,
            thread_count=1,
            fmt='jpeg',
            size=(1700, None)
        )
        total_images = len(images)
        await log(f"Successfully converted PDF: {total_images} pages")

        for idx, img in enumerate(images):
            try:
                await log(f"OCR page {idx+1}/{total_images}")
                text = pytesseract.image_to_string(img)
                await log(f"OCR complete for page {idx+1}")
                full_text += text + '\n'
                
                # Memory management
                del img
                gc.collect()
                
            except Exception as e:
                await log(f"OCR failed for page {idx+1}: {str(e)}")
                raise

        await log(f"Total extracted text length: {len(full_text)} characters")
        await log("Starting text chunking...")

        # Chunk the text
        MAX_CHUNK_SIZE = 4000
        chunks = [full_text[i:i + MAX_CHUNK_SIZE] 
                 for i in range(0, len(full_text), MAX_CHUNK_SIZE)]
        await log(f"Split into {len(chunks)} chunks")

        # Process each chunk with Ollama
        summaries = []
        for i, chunk in enumerate(chunks):

                await log(f"Processing chunk {i+1}/{len(chunks)}")
                await log(f"Chunk size: {len(chunk)} characters")
                
                # Modified Ollama call with sync handling
                response = ollama.chat(
                    model='mistral',
                    messages=[{
                        'role': 'user',
                        'content': f'Summarize this section of text concisely: {chunk}'
                    }],
                    stream=False  # Ensure we get complete response
                )
                
                summary = response['message']['content']
                await log(f"Chunk {i+1} summary length: {len(summary)} characters")
                summaries.append(summary)
                
            except Exception as e:
                await log(f"Error processing chunk {i+1}: {str(e)}")
                await log(f"Error type: {type(e)}")
                raise

        # Final summary
        if len(summaries) > 1:
            await log("Creating final summary...")
            try:
                final_response = ollama.chat(
                    model='mistral',
                    messages=[{
                        'role': 'user',
                        'content': 'Create a coherent summary from these section summaries:\n\n' + '\n\n'.join(summaries)
                    }],
                    stream=False
                )
                final_summary = final_response['message']['content']
                await log(f"Final summary length: {len(final_summary)} characters")
                return final_summary
            except Exception as e:
                await log(f"Final summary failed: {str(e)}")
                return "\n\n".join(summaries)
        else:
            return summaries[0] if summaries else "No valid summaries generated"

    except Exception as e:
        await log(f"Critical error: {str(e)}")
        raise

async def main():
    pdf_path = os.path.expanduser("~/Documents/test.pdf")
    try:
        summary = await process_pdf_test(pdf_path)
        await log("=== FINAL SUMMARY ===")
        print("\n" + summary + "\n")
    except Exception as e:
        await log(f"Test failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())