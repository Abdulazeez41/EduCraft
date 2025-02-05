from fpdf import FPDF
from datetime import datetime
import os

class CertificateGenerator:
    def __init__(self, course_name: str, student_name: str, instructor_name: str):
        self.course_name = course_name
        self.student_name = student_name
        self.instructor_name = instructor_name
        self.date = datetime.today().strftime('%Y-%m-%d')
        self.output_dir = "app/static/certificates"
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_certificate(self) -> str:
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        
        # Certificate Title
        pdf.set_font("Arial", "B", 24)
        pdf.cell(200, 20, "Certificate of Completion", ln=True, align="C")
        pdf.ln(20)
        
        # Student Name
        pdf.set_font("Arial", "B", 20)
        pdf.cell(200, 10, f"Presented to: {self.student_name}", ln=True, align="C")
        pdf.ln(10)
        
        # Course Name
        pdf.set_font("Arial", size=16)
        pdf.cell(200, 10, f"For successfully completing the course: {self.course_name}", ln=True, align="C")
        pdf.ln(20)
        
        # Instructor Signature
        pdf.cell(200, 10, f"Instructor: {self.instructor_name}", ln=True, align="C")
        pdf.ln(20)
        
        # Date
        pdf.cell(200, 10, f"Date: {self.date}", ln=True, align="C")
        
        # Save PDF
        file_name = f"{self.student_name.replace(' ', '_')}_certificate.pdf"
        file_path = os.path.join(self.output_dir, file_name)
        pdf.output(file_path)
        return file_path
