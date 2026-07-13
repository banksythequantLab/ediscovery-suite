"""The one graphic that ties the suite together: five agents -> one CockroachDB
memory -> the unified Fastow case file, with a memory OFF->ON panel beside it."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

BG="#0d1117"; INK="#e9edf2"; MUT="#8b949e"; GOLD="#f0b429"
fig, ax = plt.subplots(figsize=(16, 9)); fig.patch.set_facecolor(BG)
ax.set_xlim(0,16); ax.set_ylim(0,9); ax.axis("off"); ax.set_facecolor(BG)

def box(x,y,w,h,edge,fill="#161b22",rad=0.10,lw=2):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle=f"round,pad=0.02,rounding_size={rad}",
        linewidth=lw,edgecolor=edge,facecolor=fill)); 
def txt(x,y,s,size,color=INK,weight="bold",ha="center",va="center"):
    ax.text(x,y,s,fontsize=size,color=color,fontweight=weight,ha=ha,va=va)

ax.text(8,8.62,"Nota.Lawyer  ·  five agents, one CockroachDB memory",
        fontsize=25,color="#f0f6fc",fontweight="bold",ha="center")

# ---- LEFT: the flow ----
agents=[("Cold Case","#f85149"),("Chronicle","#d29922"),("Witness","#3fb950"),
        ("Gap Hunter","#58a6ff"),("Hold Firewall","#bc8cff")]
axx=[0.5,2.28,4.06,5.84,7.62]; aw=1.66
for (nm,c),x in zip(agents,axx):
    box(x,7.15,aw,0.95,c); txt(x+aw/2,7.62,nm,12,c)
    ax.add_patch(FancyArrowPatch((x+aw/2,7.15),(x+aw/2,5.95),arrowstyle="-|>",
        mutation_scale=13,color=MUT,lw=1.4))
# central memory band
box(0.5,4.75,8.78,1.2,GOLD,fill="#1b1a12",lw=2.6)
txt(4.89,5.55,"CockroachDB  ·  ONE transactional memory",17,"#f0f6fc")
txt(4.89,5.02,"C-SPANN vectors  ·  363K-edge graph  ·  SERIALIZABLE  ·  RLS  ·  multi-region",12,MUT,"normal")
ax.add_patch(FancyArrowPatch((4.89,4.75),(4.89,3.75),arrowstyle="-|>",mutation_scale=15,color=GOLD,lw=2))
# unified case file output
box(1.4,2.35,6.98,1.4,"#c9d1d9",fill="#12161c")
txt(4.89,3.35,"Unified Case File  —  one SQL statement",16,"#f0f6fc")
txt(4.89,2.78,"Fastow: Cold Case found nothing — the other agents caught him",12.5,GOLD,"normal")

# ---- RIGHT: memory OFF -> ON panel ----
box(9.75,2.35,5.95,5.75,"#30363d",fill="#0f1319",lw=2)
txt(12.72,7.72,"MEMORY  OFF  →  ON",17,GOLD)
txt(12.72,7.30,"same model & data — the only variable is persistence",11.5,MUT,"normal")
rows=[("Cold Case","0","4/18","#f85149"),
      ("Chronicle","0.42","0.98","#d29922"),
      ("Witness","3/12","12/12","#3fb950"),
      ("Gap Hunter","37%","100%","#58a6ff"),
      ("Hold Firewall","200","0","#bc8cff")]
y=6.55
for nm,off,on,c in rows:
    txt(10.0,y,nm,13,c,ha="left")
    txt(13.45,y,off,18,"#f85149",ha="right")
    ax.text(13.62,y,"→",fontsize=16,color=MUT,ha="center",va="center")
    txt(13.8,y,on,18,"#3fb950",ha="left")
    y-=0.92

plt.savefig(r"B:\ediscovery-suite\docs\hero.png",dpi=120,facecolor=BG,bbox_inches="tight")
print("wrote hero.png")
