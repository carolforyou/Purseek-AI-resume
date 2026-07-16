from fastapi import APIRouter
from fastapi.responses import FileResponse

from app.services.resume_export_service import ResumeExportService

router = APIRouter()
export_service = ResumeExportService()


@router.get("/resume-export/template-docx")
def export_template_docx():
    output_path = export_service.export_template_docx()
    return FileResponse(
        path=str(output_path),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename="resume-export.docx",
    )


@router.get("/resume-export/markdown")
def export_markdown():
    output_path = export_service.export_markdown_file()
    return FileResponse(
        path=str(output_path),
        media_type="text/markdown",
        filename="resume-export.md",
    )


@router.get("/resume-export/pdf")
def export_pdf():
    output_path = export_service.export_pdf()
    return FileResponse(
        path=str(output_path),
        media_type="application/pdf",
        filename="resume-export.pdf",
    )


@router.get("/resume-export/html")
def export_html():
    output_path = export_service.export_html()
    return FileResponse(
        path=str(output_path),
        media_type="text/html",
        filename="resume-preview.html",
    )