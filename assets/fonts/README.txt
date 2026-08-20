GELLIX — Displaay Type Foundry (Martin Vácha)

The five upright weights used by the page are self-hosted here, copied
from ~/Library/Fonts:

  300  Gellix-TRIAL-Light.otf
  400  Gellix-TRIAL-Regular.otf
  500  Gellix-TRIAL-Medium.otf
  600  Gellix-TRIAL-SemiBold.otf
  700  Gellix-TRIAL-Bold.otf

styles.css declares each with local() first, so your machine uses the
installed copy and skips the download; url() covers every other visitor.

BEFORE GOING LIVE
-----------------
1. These are TRIAL files — licensed for evaluation and mockups only.
   Buy the full Gellix licence from displaay.net and swap in the retail
   files (same filenames, or update the @font-face src lines).
2. Convert to woff2. The five OTFs are ~950 KB total; as woff2 that
   drops to roughly 200 KB:
     npx ttf2woff2 < Gellix-Regular.otf > Gellix-Regular.woff2
   or use https://transfonter.org — then change the src url() and
   format("opentype") to format("woff2").
3. Subset to latin if you want it smaller still.
