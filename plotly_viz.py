import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from glob import glob
import os

SEQUENCE_DIR = r"D:\Insat_data\sequences"
EVAL_DIR     = r"D:\Insat_data\evaluation"
RESULTS_DIR  = r"D:\Insat_data\results"
CH_NAMES     = ['TIR1', 'TIR2', 'WV']

os.makedirs(RESULTS_DIR, exist_ok=True)

# ── 1. Interactive sequence viewer ─────────────────────────────────────
def plot_sequence_interactive(seq_idx=0, channel=0):
    seq_path = os.path.join(SEQUENCE_DIR, f"seq_{seq_idx:03d}.npy")
    if not os.path.exists(seq_path):
        print(f"File not found: {seq_path}")
        return
    seq    = np.load(seq_path)
    labels = ['t-4', 't-3', 't-2', 't-1', 'TARGET']

    fig = make_subplots(
        rows=1, cols=5,
        subplot_titles=labels,
        horizontal_spacing=0.02
    )

    for t in range(5):
        frame = seq[t, channel]
        fig.add_trace(
            go.Heatmap(
                z=np.flipud(frame),
                colorscale='gray',
                showscale=(t == 4),
                zmin=0, zmax=1,
                name=labels[t],
                hovertemplate='Value: %{z:.3f}<extra></extra>'
            ),
            row=1, col=t+1
        )

    fig.update_layout(
        title=dict(
            text=f'INSAT-3DR Cloud Sequence | '
                 f'Channel: {CH_NAMES[channel]} | Seq {seq_idx}',
            font=dict(color='white', size=14)
        ),
        height=350,
        paper_bgcolor='#0d1117',
        plot_bgcolor='#0d1117',
        font=dict(color='white'),
    )
    fig.update_xaxes(showticklabels=False, showgrid=False)
    fig.update_yaxes(showticklabels=False, showgrid=False)

    out = os.path.join(
        RESULTS_DIR, f'sequence_{seq_idx}_interactive.html'
    )
    fig.write_html(out)
    print(f"Saved: {out}")
    return fig

# ── 2. Metrics dashboard ───────────────────────────────────────────────
def plot_metrics_dashboard():
    csv_path = os.path.join(EVAL_DIR, 'ddpm_metrics.csv')
    if not os.path.exists(csv_path):
        csv_path = os.path.join(EVAL_DIR, 'metrics.csv')
    if not os.path.exists(csv_path):
        print("metrics.csv not found. Run evaluate.py first.")
        return

    df = pd.read_csv(csv_path)

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[
            'SSIM per sample (higher is better)',
            'PSNR per sample dB (higher is better)',
            'MAE per sample (lower is better)',
            'Metric distributions'
        ],
        vertical_spacing=0.18,
        horizontal_spacing=0.12
    )

    # SSIM bar chart
    fig.add_trace(
        go.Bar(
            x=df['sample'], y=df['SSIM'],
            marker_color='cyan',
            name='SSIM',
            text=df['SSIM'].round(3),
            textposition='outside',
            hovertemplate='Sample %{x}<br>SSIM: %{y:.4f}<extra></extra>'
        ),
        row=1, col=1
    )
    fig.add_hline(
        y=df['SSIM'].mean(),
        line_dash="dash",
        line_color="yellow",
        annotation_text=f"Mean={df['SSIM'].mean():.4f}",
        annotation_font_color="yellow",
        row=1, col=1
    )

    # PSNR bar chart
    fig.add_trace(
        go.Bar(
            x=df['sample'], y=df['PSNR'],
            marker_color='lime',
            name='PSNR',
            text=df['PSNR'].round(1),
            textposition='outside',
            hovertemplate='Sample %{x}<br>PSNR: %{y:.2f}dB<extra></extra>'
        ),
        row=1, col=2
    )
    fig.add_hline(
        y=df['PSNR'].mean(),
        line_dash="dash",
        line_color="yellow",
        annotation_text=f"Mean={df['PSNR'].mean():.2f}dB",
        annotation_font_color="yellow",
        row=1, col=2
    )

    # MAE bar chart
    fig.add_trace(
        go.Bar(
            x=df['sample'], y=df['MAE'],
            marker_color='orange',
            name='MAE',
            text=df['MAE'].round(4),
            textposition='outside',
            hovertemplate='Sample %{x}<br>MAE: %{y:.4f}<extra></extra>'
        ),
        row=2, col=1
    )
    fig.add_hline(
        y=df['MAE'].mean(),
        line_dash="dash",
        line_color="yellow",
        annotation_text=f"Mean={df['MAE'].mean():.4f}",
        annotation_font_color="yellow",
        row=2, col=1
    )

    # Box plots
    for col_name, color in zip(
        ['SSIM', 'PSNR', 'MAE'],
        ['cyan', 'lime', 'orange']
    ):
        fig.add_trace(
            go.Box(
                y=df[col_name],
                name=col_name,
                marker_color=color,
                boxmean=True,
                hovertemplate='%{y:.4f}<extra></extra>'
            ),
            row=2, col=2
        )

    fig.update_layout(
        title=dict(
            text='Chase the Cloud — Evaluation Metrics Dashboard',
            font=dict(color='white', size=16)
        ),
        height=650,
        paper_bgcolor='#0d1117',
        plot_bgcolor='#161b22',
        font=dict(color='white', size=11),
        showlegend=False,
    )
    fig.update_xaxes(
        gridcolor='#30363d', title_font=dict(color='white')
    )
    fig.update_yaxes(
        gridcolor='#30363d', title_font=dict(color='white')
    )

    out = os.path.join(RESULTS_DIR, 'metrics_dashboard.html')
    fig.write_html(out)
    print(f"Saved: {out}")
    return fig

# ── 3. Cloud motion animation ──────────────────────────────────────────
def plot_cloud_animation(seq_idx=0, channel=0):
    seq_path = os.path.join(SEQUENCE_DIR, f"seq_{seq_idx:03d}.npy")
    if not os.path.exists(seq_path):
        print(f"File not found: {seq_path}")
        return

    seq    = np.load(seq_path)
    labels = ['t-4 (oldest)', 't-3', 't-2', 't-1 (latest)', 'TARGET (future)']
    colors = ['gray', 'gray', 'gray', 'gray', 'Viridis']

    frames = []
    for t in range(5):
        frames.append(
            go.Frame(
                data=[go.Heatmap(
                    z=np.flipud(seq[t, channel]),
                    colorscale=colors[t],
                    zmin=0, zmax=1,
                    showscale=True,
                    colorbar=dict(
                        title='Intensity',
                        titlefont=dict(color='white'),
                        tickfont=dict(color='white')
                    )
                )],
                name=str(t),
                layout=go.Layout(
                    title_text=f'Cloud Motion | {labels[t]} | '
                               f'Channel: {CH_NAMES[channel]}'
                )
            )
        )

    fig = go.Figure(
        data=[go.Heatmap(
            z=np.flipud(seq[0, channel]),
            colorscale='gray',
            zmin=0, zmax=1,
            showscale=True
        )],
        frames=frames,
        layout=go.Layout(
            title=dict(
                text=f'Cloud Motion Animation — {CH_NAMES[channel]} Channel',
                font=dict(color='white', size=14)
            ),
            height=520,
            paper_bgcolor='#0d1117',
            plot_bgcolor='#0d1117',
            font=dict(color='white'),
            xaxis=dict(showticklabels=False, showgrid=False),
            yaxis=dict(showticklabels=False, showgrid=False),
            updatemenus=[{
                "type"      : "buttons",
                "showactive": False,
                "y"         : 1.15,
                "x"         : 0.5,
                "xanchor"   : "center",
                "bgcolor"   : "#21262d",
                "bordercolor": "#30363d",
                "buttons"   : [
                    {
                        "label" : "Play",
                        "method": "animate",
                        "args"  : [None, {
                            "frame"      : {
                                "duration": 700,
                                "redraw"  : True
                            },
                            "fromcurrent": True,
                            "transition" : {"duration": 300}
                        }]
                    },
                    {
                        "label" : "Pause",
                        "method": "animate",
                        "args"  : [[None], {
                            "frame"     : {
                                "duration": 0,
                                "redraw"  : False
                            },
                            "mode"      : "immediate",
                            "transition": {"duration": 0}
                        }]
                    }
                ]
            }],
            sliders=[{
                "active": 0,
                "bgcolor": "#21262d",
                "bordercolor": "#30363d",
                "font"  : {"color": "white"},
                "steps" : [
                    {
                        "method": "animate",
                        "args"  : [[str(t)], {
                            "frame"     : {
                                "duration": 300,
                                "redraw"  : True
                            },
                            "mode"      : "immediate",
                            "transition": {"duration": 100}
                        }],
                        "label" : labels[t]
                    }
                    for t in range(5)
                ],
                "currentvalue": {
                    "prefix"  : "Frame: ",
                    "font"    : {"color": "white"},
                    "visible" : True
                },
                "y"    : 0,
                "len"  : 1.0
            }]
        )
    )

    out = os.path.join(
        RESULTS_DIR, f'cloud_animation_{seq_idx}.html'
    )
    fig.write_html(out)
    print(f"Saved: {out}")
    return fig

# ── 4. Performance gauge dashboard ────────────────────────────────────
def plot_summary_gauges():
    csv_path = os.path.join(EVAL_DIR, 'ddpm_metrics.csv')
    if not os.path.exists(csv_path):
        csv_path = os.path.join(EVAL_DIR, 'metrics.csv')
    if not os.path.exists(csv_path):
        print("metrics.csv not found.")
        return

    df = pd.read_csv(csv_path)

    fig = make_subplots(
        rows=1, cols=3,
        specs=[[
            {"type": "indicator"},
            {"type": "indicator"},
            {"type": "indicator"}
        ]],
        subplot_titles=['SSIM', 'PSNR (dB)', 'MAE']
    )

    fig.add_trace(go.Indicator(
        mode  = "gauge+number+delta",
        value = df['SSIM'].mean(),
        title = {"text": "Mean SSIM", "font": {"color": "white"}},
        number= {"font": {"color": "cyan"}},
        delta = {"reference": 0.6, "increasing": {"color": "lime"}},
        gauge = {
            "axis"     : {"range": [0, 1], "tickcolor": "white"},
            "bar"      : {"color": "cyan"},
            "bgcolor"  : "#161b22",
            "bordercolor": "#30363d",
            "steps"    : [
                {"range": [0.0, 0.6], "color": "#3d0000"},
                {"range": [0.6, 0.8], "color": "#3d2000"},
                {"range": [0.8, 1.0], "color": "#003d00"},
            ],
            "threshold": {
                "line" : {"color": "white", "width": 3},
                "value": 0.6
            }
        },
        domain={"row": 0, "column": 0}
    ), row=1, col=1)

    fig.add_trace(go.Indicator(
        mode  = "gauge+number+delta",
        value = df['PSNR'].mean(),
        title = {"text": "Mean PSNR (dB)", "font": {"color": "white"}},
        number= {"font": {"color": "lime"}, "suffix": " dB"},
        delta = {"reference": 25, "increasing": {"color": "lime"}},
        gauge = {
            "axis"     : {"range": [0, 50], "tickcolor": "white"},
            "bar"      : {"color": "lime"},
            "bgcolor"  : "#161b22",
            "bordercolor": "#30363d",
            "steps"    : [
                {"range": [0,  25], "color": "#3d0000"},
                {"range": [25, 35], "color": "#3d2000"},
                {"range": [35, 50], "color": "#003d00"},
            ],
            "threshold": {
                "line" : {"color": "white", "width": 3},
                "value": 25
            }
        },
        domain={"row": 0, "column": 1}
    ), row=1, col=2)

    fig.add_trace(go.Indicator(
        mode  = "gauge+number",
        value = df['MAE'].mean(),
        title = {"text": "Mean MAE", "font": {"color": "white"}},
        number= {"font": {"color": "orange"}},
        gauge = {
            "axis"     : {
                "range"    : [0, 0.1],
                "tickcolor": "white"
            },
            "bar"      : {"color": "orange"},
            "bgcolor"  : "#161b22",
            "bordercolor": "#30363d",
            "steps"    : [
                {"range": [0,    0.02], "color": "#003d00"},
                {"range": [0.02, 0.05], "color": "#3d2000"},
                {"range": [0.05, 0.1],  "color": "#3d0000"},
            ],
            "threshold": {
                "line" : {"color": "white", "width": 3},
                "value": 0.05
            }
        },
        domain={"row": 0, "column": 2}
    ), row=1, col=3)

    fig.update_layout(
        title=dict(
            text='Chase the Cloud — Model Performance Summary',
            font=dict(color='white', size=16)
        ),
        height=400,
        paper_bgcolor='#0d1117',
        font=dict(color='white'),
        margin=dict(t=80, b=20)
    )

    out = os.path.join(RESULTS_DIR, 'performance_summary.html')
    fig.write_html(out)
    print(f"Saved: {out}")
    return fig

# ── 5. Multi-sequence comparison ──────────────────────────────────────
def plot_multi_sequence(n_seqs=5, channel=0):
    seq_files = sorted(
        glob(os.path.join(SEQUENCE_DIR, "*.npy"))
    )[:n_seqs]

    fig = make_subplots(
        rows=n_seqs, cols=5,
        subplot_titles=[
            f'Seq {i} | {l}'
            for i in range(n_seqs)
            for l in ['t-4','t-3','t-2','t-1','TARGET']
        ],
        vertical_spacing=0.05,
        horizontal_spacing=0.02
    )

    for row, sf in enumerate(seq_files, 1):
        seq = np.load(sf)
        for t in range(5):
            fig.add_trace(
                go.Heatmap(
                    z=np.flipud(seq[t, channel]),
                    colorscale='gray',
                    zmin=0, zmax=1,
                    showscale=False
                ),
                row=row, col=t+1
            )

    fig.update_layout(
        title=dict(
            text=f'Multi-sequence View | Channel: {CH_NAMES[channel]}',
            font=dict(color='white', size=14)
        ),
        height=200 * n_seqs,
        paper_bgcolor='#0d1117',
        plot_bgcolor='#0d1117',
        font=dict(color='white'),
    )
    fig.update_xaxes(showticklabels=False, showgrid=False)
    fig.update_yaxes(showticklabels=False, showgrid=False)

    out = os.path.join(RESULTS_DIR, 'multi_sequence_view.html')
    fig.write_html(out)
    print(f"Saved: {out}")
    return fig

# ── Main ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Generating Plotly visualizations...\n")

    print("1. Interactive sequence viewer...")
    plot_sequence_interactive(seq_idx=0, channel=0)

    print("2. Metrics dashboard...")
    plot_metrics_dashboard()

    print("3. Cloud motion animation...")
    plot_cloud_animation(seq_idx=0, channel=0)

    print("4. Performance summary gauges...")
    plot_summary_gauges()

    print("5. Multi-sequence comparison...")
    plot_multi_sequence(n_seqs=5, channel=0)

    print(f"\nAll visualizations saved to {RESULTS_DIR}")
    print("Open .html files in Chrome for interactive viewing.")