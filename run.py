from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from datetime import datetime
import os

app = FastAPI(title="Advanced HTML File Server")

HTML_DIR = Path("html_files")
HTML_DIR.mkdir(exist_ok=True)

# Если нужна поддержка статических файлов (CSS, JS, изображения)
# app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/{file_number}")
async def get_html_by_number(file_number: str, request: Request):
    """
    Отдает HTML-файл по номеру с проверкой безопасности
    """
    # Очистка от опасных символов
    clean_number = "".join(c for c in file_number if c.isdigit())
    
    if not clean_number:
        raise HTTPException(status_code=400, detail="Номер файла должен содержать цифры")
    
    # Ограничение на длину номера (защита от перебора)
    if len(clean_number) > 10:
        raise HTTPException(status_code=400, detail="Слишком длинный номер файла")
    
    file_name = f"{clean_number}.html"
    file_path = HTML_DIR / file_name
    
    if not file_path.exists():
        # Можно также искать файлы с другими расширениями
        alternatives = list(HTML_DIR.glob(f"{clean_number}.*"))
        if alternatives:
            return FileResponse(alternatives[0])
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Файл {file_name} не найден"
            )
    
    # Добавляем заголовки для безопасности
    headers = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "SAMEORIGIN",
    }
    
    return FileResponse(
        file_path,
        media_type="text/html",
        headers=headers
    )

@app.get("/")
async def root(request: Request):
    """Главная с информацией о сервере"""
    html_files = sorted(HTML_DIR.glob("*.html"))
    
    files_html = ""
    for f in html_files:
        size = f.stat().st_size
        size_str = f"{size:,} bytes" if size < 1024 else f"{size/1024:.1f} KB"
        mtime = datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        files_html += f"""
        <tr>
            <td><a href="/{f.stem}">📄 {f.name}</a></td>
            <td>{size_str}</td>
            <td>{mtime}</td>
        </tr>"""
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>HTML Files Server</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: 'Segoe UI', Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }}
            .container {{
                max-width: 900px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                padding: 40px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #333;
                margin-bottom: 10px;
                font-size: 2.5em;
            }}
            .subtitle {{
                color: #666;
                margin-bottom: 30px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            th {{
                background: #f8f9fa;
                padding: 15px;
                text-align: left;
                border-bottom: 2px solid #dee2e6;
            }}
            td {{
                padding: 12px 15px;
                border-bottom: 1px solid #f0f0f0;
            }}
            tr:hover {{
                background: #f8f9fa;
            }}
            a {{
                color: #667eea;
                text-decoration: none;
                font-weight: 500;
            }}
            a:hover {{
                text-decoration: underline;
            }}
            .quick-access {{
                margin-top: 30px;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 10px;
            }}
            .quick-access input {{
                padding: 10px;
                border: 2px solid #dee2e6;
                border-radius: 5px;
                font-size: 16px;
                width: 200px;
            }}
            .quick-access button {{
                padding: 10px 20px;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 HTML File Server</h1>
            <p class="subtitle">Доступ к файлам по номеру: /номер</p>
            
            <table>
                <thead>
                    <tr>
                        <th>Файл</th>
                        <th>Размер</th>
                        <th>Изменен</th>
                    </tr>
                </thead>
                <tbody>
                    {files_html if files_html else '<tr><td colspan="3">Нет доступных файлов</td></tr>'}
                </tbody>
            </table>
            
            <div class="quick-access">
                <h3>Быстрый доступ:</h3>
                <input type="number" id="fileNumber" placeholder="Номер файла" min="0">
                <button onclick="openFile()">Открыть</button>
            </div>
        </div>
        
        <script>
            function openFile() {{
                const num = document.getElementById('fileNumber').value;
                if (num) {{
                    window.location.href = '/' + num;
                }}
            }}
            document.getElementById('fileNumber').addEventListener('keypress', function(e) {{
                if (e.key === 'Enter') openFile();
            }});
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

# Для запуска с разными настройками
if __name__ == "__main__":
    import uvicorn
    import argparse
    
    parser = argparse.ArgumentParser(description='HTML File Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind')
    parser.add_argument('--port', type=int, default=8888, help='Port to bind')
    parser.add_argument('--dir', default='html_files', help='Directory with HTML files')
    
    args = parser.parse_args()
    HTML_DIR = Path(args.dir)
    HTML_DIR.mkdir(exist_ok=True)
    
    print(f"📁 Serving files from: {HTML_DIR.absolute()}")
    print(f"🌐 Server starting at http://{args.host}:{args.port}")
    
    uvicorn.run(app, host=args.host, port=args.port)