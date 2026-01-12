# # utils/pdf_generator.py

# from fpdf import FPDF
# import datetime

# class TextilePDF(FPDF):
#     def header(self):
#         # Centering the Collection Name (e.g., LINEN TUBE) in the header 
#         self.set_font("helvetica", "B", 16)
#         # Use getattr to safely access collection_name set during generation
#         title = getattr(self, 'collection_name', 'COLLECTION')
#         self.cell(0, 10, title, align="C") # Center alignment 
#         self.ln(15)

#     def footer(self):
#         self.set_y(-15)
#         self.set_font("helvetica", "I", 8)
#         self.cell(0, 10, f"Page {self.page_no()} | {self.collection_name}", align="C")

# def create_unified_catalog(ai_images, cad_images, collection_name):
#     pdf = TextilePDF()
#     pdf.collection_name = collection_name
#     # Increased bottom margin to ensure space at the end of the page 
#     pdf.set_auto_page_break(auto=True, margin=20) 

#     # --- SECTION 1: AI LOOKBOOK ---
#     # Standardizing image size and adding spacing 
#     img_w = 170
#     x_centered = (210 - img_w) / 2 # Centering on A4 (210mm wide)
    
#     for i in range(0, len(ai_images), 2):
#         pdf.add_page()
        
#         # Image 1 (Top)
#         pdf.image(ai_images[i], x=x_centered, y=35, w=img_w)
        
#         # Image 2 (Bottom) with clear spacing between them 
#         if i + 1 < len(ai_images):
#             # y=145 provides a consistent gap and space before the footer 
#             pdf.image(ai_images[i+1], x=x_centered, y=145, w=img_w)

#     # --- SECTION 2: CAD PATTERNS ---
#     # Uploaded CAD images are kept as-is, one per page, no snipping 
#     for cad in cad_images:
#         pdf.add_page()
        
#         # Centering the original CAD image 
#         cad_w = 180
#         cad_x = (210 - cad_w) / 2
#         # Center vertically and remove all extra text labels 
#         pdf.image(cad, x=cad_x, y=45, w=cad_w)
            
#     return pdf.output()



# utils/pdf_generator.py

from fpdf import FPDF

class TextilePDF(FPDF):
    def header(self):
        # 1. Company Logo - TOP RIGHT
        if hasattr(self, 'logo_path') and self.logo_path:
            try:
                # Page width is 210mm. 210 - 40 (image width) - 10 (margin) = 160
                self.image(self.logo_path, 160, 8, 40)
            except: pass
        
        # 2. Collection Name - CENTERED
        self.set_font("helvetica", "B", 16)
        self.set_text_color(0, 0, 0) # Black
        title = getattr(self, 'collection_name', 'COLLECTION')
        self.set_y(10)
        self.cell(0, 10, title, align="C") 
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "B", 10)
        
        # Calculate total width for centering
        brand = getattr(self, 'company_name', 'Textile Studio')
        prefix = "A product by - "
        full_text_w = self.get_string_width(prefix + brand)
        start_x = (210 - full_text_w) / 2
        
        # 3. "A product by" - BLUE FONT
        self.set_x(start_x)
        self.set_text_color(0, 0, 255) # Blue (R, G, B)
        self.write(10, prefix)
        
        # 4. "Company Name" - RED FONT
        self.set_text_color(255, 0, 0) # Red (R, G, B)
        self.write(10, brand)

def create_unified_catalog(ai_images, cad_images, collection_name, company_name, logo_path):
    pdf = TextilePDF()
    pdf.collection_name = collection_name
    pdf.company_name = company_name
    pdf.logo_path = logo_path
    
    # PAGE 1: FULL PAGE MODEL HERO
    pdf.add_page()
    pdf.image(ai_images[0], x=10, y=35, w=190)

    # PAGE 2: TWO UNIQUE SHIRT FLATLAYS (From different CADs)
    pdf.add_page()
    img_w = 120
    x_centered = (210 - img_w) / 2
    
    if len(ai_images) > 1:
        pdf.image(ai_images[1], x=x_centered, y=35, w=img_w)
    if len(ai_images) > 2:
        pdf.image(ai_images[2], x=x_centered, y=160, w=img_w)

    # PAGES 3-14: TECHNICAL PATTERNS
    for cad in cad_images:
        pdf.add_page()
        pdf.image(cad, x=12.5, y=25, w=185)
            
    return pdf.output()