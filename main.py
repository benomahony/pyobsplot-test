import polars as pl
from pyobsplot import Plot
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import io

app = FastAPI()

templates = Jinja2Templates(directory="templates")


penguins = pl.read_csv("https://github.com/juba/pyobsplot/raw/main/doc/data/penguins.csv")

def generate_plot_spec(opacity=1.0):
    """Generate the plot specification with given opacity"""
    return {
        "grid": True,
        "marks": [
            Plot.rectY(
                penguins,
                Plot.binX(
                    {"y": "count"},
                    {"x": "body_mass_g", "fill": "steelblue", "fillOpacity": opacity},
                ),
            ),
            Plot.ruleY([0]),
        ],
    }

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the main page with the initial plot and opacity slider"""
    return templates.TemplateResponse(
        "index.html", 
        {"request": request}
    )

@app.get("/plot", response_class=HTMLResponse)
async def get_plot(opacity: float = 1.0):
    """Generate plot with the specified opacity"""
    html_output = io.StringIO()
    
    Plot.plot(
        format="html",
        path=html_output,
        spec=generate_plot_spec(opacity)
    )
    
    html_content = html_output.getvalue()
    return html_content

@app.post("/update-plot", response_class=HTMLResponse)
async def update_plot(opacity: float = Form(...)):
    """htmx endpoint to update the plot with a new opacity"""
    html_output = io.StringIO()
    
    Plot.plot(
        format="html",
        path=html_output,
        spec=generate_plot_spec(opacity / 100)
    )
    
    html_content = html_output.getvalue()
    return html_content
