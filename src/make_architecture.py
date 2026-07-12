"""Entwinement architecture: five agents, one CockroachDB memory."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

BG="#0d1117"; FG="#e6edf3"; MUT="#8b949e"; LINE="#30363d"
fig, ax = plt.subplots(figsize=(15, 9)); fig.patch.set_facecolor(BG); ax.set_facecolor(BG)
ax.set_xlim(0,15); ax.set_ylim(0,9); ax.axis("off")

def box(x,y,w,h,title,sub,edge,fill="#161b22",tsize=13,ssize=9.5):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.04,rounding_size=0.12",
        linewidth=2,edgecolor=edge,facecolor=fill))
    ax.text(x+w/2,y+h-0.32,title,ha="center",va="top",color=FG,fontsize=tsize,fontweight="bold")
    if sub: ax.text(x+w/2,y+h-0.72,sub,ha="center",va="top",color=MUT,fontsize=ssize)

# shared memory band (top)
box(0.6,6.9,13.8,1.7,"CockroachDB  ·  ONE database (coldcase)",
    "persons + 500K emails  ·  C-SPANN vectors  ·  communication graph  ·  transactional case memory  ·  SERIALIZABLE / ACID",
    "#c9a227",fill="#1b1a12",tsize=16,ssize=11)

# five agents (middle row)
agents = [
 ("Cold Case","investigate → suspects","#f85149"),
 ("Chronicle","living theory / timeline","#d29922"),
 ("Witness","impeachment file","#3fb950"),
 ("Gap Hunter","what's missing","#58a6ff"),
 ("Hold Firewall","ACID spoliation guard","#bc8cff"),
]
xs=[0.6,3.42,6.24,9.06,11.88]; w=2.7
for (t,s,c),x in zip(agents,xs):
    box(x,3.7,w,1.5,t,s,c)
    # read (down from memory) + write (up to memory) arrows
    ax.add_patch(FancyArrowPatch((x+w*0.36,5.2),(x+w*0.36,6.9),arrowstyle="-|>",mutation_scale=14,color=MUT,lw=1.4))
    ax.add_patch(FancyArrowPatch((x+w*0.64,6.9),(x+w*0.64,5.2),arrowstyle="-|>",mutation_scale=14,color=c,lw=1.6))

ax.text(7.5,5.55,"every agent READS and WRITES the same memory",ha="center",color=MUT,fontsize=10,style="italic")

# unified query band (bottom)
box(0.6,1.15,13.8,1.7,"ONE SQL statement  →  unified case file",
    "Skilling: Cold Case 0.99 + 4 contradictions + 4 timeline events + 2 missing docs        "
    "Fastow: Cold Case MISSED him — but Witness, Chronicle & Gap Hunter caught him",
    "#8b949e",fill="#12161c",tsize=15,ssize=10.5)
for x in xs:
    ax.add_patch(FancyArrowPatch((x+w/2,3.7),(x+w/2,2.85),arrowstyle="-|>",mutation_scale=13,color=LINE,lw=1.3))

fig.suptitle("Nota.Lawyer  ·  a CockroachDB E-Discovery Suite  ·  five agents, one entwined memory",
             color="#f0f6fc",fontsize=19,y=0.97)
plt.savefig(r"B:\ediscovery-suite\docs\architecture.png",dpi=130,facecolor=BG,bbox_inches="tight")
print("wrote architecture.png")
