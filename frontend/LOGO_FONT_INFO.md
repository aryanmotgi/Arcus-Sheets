# ARCUS Logo Font Information

## Current Font Stack:
The app uses this font order (first available will be used):
1. **Uncial Antiqua** - Gothic/blackletter style font from Google Fonts
2. **Ewert** - Another decorative serif font
3. **MedievalSharp** - Medieval-inspired font
4. **Times New Roman** - System fallback

## To Use Your Exact Font:

If you have the exact font file from your image:

1. **Place font file** in `frontend/fonts/` folder (create the folder if needed)
   - Name it something like `arcus-font.ttf` or `arcus-font.otf`

2. **Add @font-face to styles.css**:
   ```css
   @font-face {
       font-family: 'ArcusFont';
       src: url('./fonts/arcus-font.ttf') format('truetype');
       font-weight: normal;
       font-style: normal;
   }
   ```

3. **Update logo-text class** to use your font:
   ```css
   .logo-text {
       font-family: 'ArcusFont', 'Uncial Antiqua', serif;
   }
   ```

## App Icons Created:
- `icon-192.png` - For app icon (192x192)
- `icon-512.png` - For app icon (512x512)

These icons show "ARCUS" in white text on black background and will appear when you add the app to your iPhone home screen.

## Font Name Needed:
If you can tell me the exact name of the font used in your image, I can help you find it or create a better CSS match!
