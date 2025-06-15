#!/usr/bin/env python3
"""
Simple test script to verify markdown file processing
Tests the core functionality without external dependencies
"""

import os
import re
from pathlib import Path

def extract_title_from_filename(filename: str) -> str:
    """Extract clean title from filename."""
    # Remove the UUID at the end and .md extension
    title = filename.replace('.md', '')
    # Split by space and remove last part if it looks like a UUID
    parts = title.split(' ')
    if len(parts) > 1 and len(parts[-1]) == 32 and parts[-1].isalnum():
        title = ' '.join(parts[:-1])
    return title

def clean_markdown_content(content: str) -> str:
    """Clean and normalize markdown content."""
    # Remove excessive whitespace
    content = re.sub(r'\n\s*\n', '\n\n', content)
    
    # Convert markdown headers to clean text
    content = re.sub(r'^#{1,6}\s*', '', content, flags=re.MULTILINE)
    
    # Remove markdown formatting but keep structure
    content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)  # Bold
    content = re.sub(r'\*(.*?)\*', r'\1', content)      # Italic
    content = re.sub(r'`(.*?)`', r'\1', content)        # Code
    
    # Clean up bullet points
    content = re.sub(r'^[\-\*\+]\s+', '• ', content, flags=re.MULTILINE)
    
    return content.strip()

def determine_specialty_from_filename(filename: str) -> str:
    """Determine medical specialty from filename."""
    filename_lower = filename.lower()
    
    # Specialty mappings
    specialty_keywords = {
        "reumatologia": ["artritis", "lupus", "vasculitis", "articular", "reumat", "espondiloartritis", 
                       "polimialgia", "miopat", "miositis", "cristales", "osteoporosis", "biologico",
                       "dolor", "inflamatorio"],
        "cardiologia": ["cardiaca", "cardiolog", "coronario", "arritmia", "fibrilacion", "hipertension",
                      "aortic", "valvular", "infarto", "angina"],
        "endocrinologia": ["diabetes", "tiroides", "suprarrenal", "acromegalia", "hipoglicemia",
                         "hiperglicemia", "insulina", "endocrin"],
        "nefrologia": ["renal", "nefr", "dialisis", "glomerulo", "proteinuria", "hiponatremia",
                      "hipokalemia", "hiperkalemia", "riñon"],
        "hematologia": ["anemia", "leucemia", "linfoma", "trombocit", "hemolisis", "coagulacion",
                      "hematolog", "mieloma", "hemograma", "ferritina"],
        "infectologia": ["antibiot", "antimicrobiano", "infeccion", "vih", "tuberculosis", "microbio",
                       "resistencia", "gram", "fungic"],
        "neurologia": ["neurologico", "acv", "encef", "mening", "neuropat", "convulsion", "cefalea"],
        "gastroenterologia": ["hepat", "cirrosis", "gastro", "esofag", "nutric", "disfagia"],
        "medicina_interna": ["hospitalizado", "intensivo", "shock", "medicina interna", "general"]
    }
    
    for specialty, keywords in specialty_keywords.items():
        if any(keyword in filename_lower for keyword in keywords):
            return specialty
    
    return "medicina_general"

def split_text_into_chunks(text: str, max_chunk_size: int = 1000):
    """Split text into manageable chunks."""
    # Split by paragraphs first
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = ""
    
    for paragraph in paragraphs:
        # If adding this paragraph would exceed max size, start new chunk
        if len(current_chunk) + len(paragraph) > max_chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            current_chunk = paragraph
        else:
            current_chunk += "\n\n" + paragraph if current_chunk else paragraph
    
    # Add the last chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks

def test_markdown_processing():
    """Test the markdown processing functionality."""
    
    # Path to the embeddings directory
    embeddings_dir = Path(__file__).parent.parent.parent / "Material para embeddings"
    
    print(f"🔍 Testing markdown processing...")
    print(f"📁 Embeddings directory: {embeddings_dir}")
    print(f"📁 Directory exists: {embeddings_dir.exists()}")
    
    if not embeddings_dir.exists():
        print(f"❌ Directory not found: {embeddings_dir}")
        return
    
    # Get all markdown files
    markdown_files = list(embeddings_dir.glob("*.md"))
    print(f"📚 Found {len(markdown_files)} markdown files")
    
    # Process a few sample files
    processed_count = 0
    for md_file in markdown_files[:5]:  # Test first 5 files
        try:
            print(f"\n🔄 Processing: {md_file.name}")
            
            # Extract title
            title = extract_title_from_filename(md_file.name)
            print(f"📝 Title: {title}")
            
            # Determine specialty
            specialty = determine_specialty_from_filename(md_file.name)
            print(f"🏥 Specialty: {specialty}")
            
            # Read and process content
            with open(md_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Clean content
            cleaned_content = clean_markdown_content(content)
            print(f"📄 Original length: {len(content)} chars")
            print(f"🧹 Cleaned length: {len(cleaned_content)} chars")
            
            # Split into chunks
            chunks = split_text_into_chunks(cleaned_content)
            print(f"🧩 Chunks created: {len(chunks)}")
            
            # Show first chunk preview
            if chunks:
                preview = chunks[0][:200] + "..." if len(chunks[0]) > 200 else chunks[0]
                print(f"👀 First chunk preview: {preview}")
            
            processed_count += 1
            print(f"✅ Successfully processed!")
            
        except Exception as e:
            print(f"❌ Error processing {md_file.name}: {e}")
    
    print(f"\n📊 SUMMARY:")
    print(f"✅ Successfully processed: {processed_count} files")
    print(f"📚 Total files found: {len(markdown_files)}")
    print(f"🎉 Processing test completed!")

if __name__ == "__main__":
    test_markdown_processing()