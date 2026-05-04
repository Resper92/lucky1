from fastapi import FastAPI, Request, Form ,HTTPException ,Depends
from fastapi.responses import HTMLResponse, RedirectResponse
import uvicorn
from fastapi.templating import Jinja2Templates 
from fastapi.staticfiles import StaticFiles
from conectdb_Roman import db_session , get_db
from model import User
from sqlalchemy import func
from sqlalchemy.orm import Session


app = FastAPI()
app.mount("/css", StaticFiles(directory="css"), name="css")

templates = Jinja2Templates(directory="templates")

def get_admin_user(request: Request, db: Session = Depends(get_db)):
    user_id = request.cookies.get("admin_session")
    if not user_id:
        return None
    
    user = db.query(User).filter(User.user_id == int(user_id)).first()
    if user and user.is_admin:
        return user
    return None

@app.get("/",response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/loghin",response_class=HTMLResponse)
async def loghin(request: Request):
    return templates.TemplateResponse(request=request, name="loghin.html")

@app.post("/do_loghin")
async def do_loghin(username: str = Form(...),
                    user_id: int = Form(...),
                    db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username,
                                 User.user_id == user_id, 
                                 User.is_admin == True).first()
    if not user:
        print(f"DEBUG: Cerco username={username} e id={user_id}")
        return RedirectResponse(url="/", status_code=302)
    
    
    response = RedirectResponse(url="/admin", status_code=303)
    response.set_cookie(key="admin_session", value=str(user.user_id), httponly=True)
    return response
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)