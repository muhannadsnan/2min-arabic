"""crop.py in.png out.png cx_frac top_frac height_frac  → 576x1024 crop (9:16) of a keyframe."""
import sys
from PIL import Image
im=Image.open(sys.argv[1]).convert("RGB"); W,H=im.size
cx,top,hf=map(float,sys.argv[3:6])
h=H*hf; w=h*9/16
x0=max(0,min(W-w,cx*W-w/2)); y0=max(0,min(H-h,top*H))
im.crop((int(x0),int(y0),int(x0+w),int(y0+h))).resize((576,1024),Image.LANCZOS).save(sys.argv[2])
