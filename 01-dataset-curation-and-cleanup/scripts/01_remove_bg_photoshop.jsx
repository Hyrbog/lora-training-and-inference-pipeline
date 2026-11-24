// ============================================================================
// Batch Background Removal Script for Adobe Photoshop (ExtendScript)
// Part of Phase 01: Dataset Curation & Cleanup
// ============================================================================

// --- SILENT MODE & PERFORMANCE ---
app.displayDialogs = DialogModes.NO;

// --- WORKING DIRECTORIES (Standardized Pipeline Structure) ---
// Expected folder layout inside ComfyUI/input:
//   DataSetPONY/
//     ├── conFondo/      (Input: curated images with original background)
//     ├── sinFondo/      (Output: transparent PNG cutouts)
//     └── fondoBlanco/   (Output: pure white background for Pony training)

var origenDir = new Folder("./input/DataSetPONY/conFondo");
var destinoDir = new Folder("./input/DataSetPONY/sinFondo");

// Create output directory if it does not exist
if (!destinoDir.exists) {
    destinoDir.create();
}

// Scan all supported images in input folder
var archivos = origenDir.getFiles(/\.(jpg|jpeg|png|webp)$/i);
var totalProcesados = 0;
var errores = 0;

for (var i = 0; i < archivos.length; i++) {
    var archivoActual = archivos[i];

    // Format output filename as PNG
    var nombreLimpio = archivoActual.name.substring(0, archivoActual.name.lastIndexOf("."));
    var rutaFinal = destinoDir.fsName + "/" + nombreLimpio + ".png";
    var archivoDestino = new File(rutaFinal);

    // Skip if already processed (idempotent execution)
    if (archivoDestino.exists) continue;

    try {
        // 1. Open source image
        var doc = app.open(archivoActual);

        // 2. Enforce native RGB color mode
        if (doc.mode != DocumentMode.RGB) {
            doc.changeMode(ChangeMode.RGB);
        }

        // 3. Unlock background layer to enable alpha transparency
        var capaOriginal = doc.activeLayer;
        var nuevaCapa = capaOriginal.duplicate();
        nuevaCapa.name = "Transparent_Canvas";

        try {
            doc.backgroundLayer.remove();
        } catch (e) {
            capaOriginal.remove();
        }

        // 4. AI Subject Selection (universal ExtendScript action)
        var idAutoCutout = stringIDToTypeID("autoCutout");
        var desc = new ActionDescriptor();
        executeAction(idAutoCutout, desc, DialogModes.NO);

        // 5. Invert selection to target the background
        doc.selection.invert();

        // 6. Delete background pixels
        doc.selection.clear();

        // 7. Clear active selection
        doc.selection.deselect();

        // 8. Save as lossless transparent PNG
        var opcionesPng = new PNGSaveOptions();
        opcionesPng.compression = 5;
        opcionesPng.interlaced = false;
        doc.saveAs(archivoDestino, opcionesPng, true, Extension.LOWERCASE);

        // 9. Close document without altering source
        doc.close(SaveOptions.DONOTSAVECHANGES);

        // 10. Purge history & clipboard to prevent RAM bloat on large batches
        app.purge(PurgeTarget.HISTORY);
        app.purge(PurgeTarget.CLIPBOARD);
        totalProcesados++;

    } catch (error) {
        errores++;
        try {
            app.activeDocument.close(SaveOptions.DONOTSAVECHANGES);
            app.purge(PurgeTarget.ALLPURGES);
        } catch (e) {}
    }
}

// Restore Photoshop dialogs
app.displayDialogs = DialogModes.ALL;

// Final summary report
alert("BATCH PROCESSING COMPLETE!\n\nImages processed: " + totalProcesados + "\nErrors: " + errores + "\n\nTransparent PNGs saved to: " + destinoDir.fsName);