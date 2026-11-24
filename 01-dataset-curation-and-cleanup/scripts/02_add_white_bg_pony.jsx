// ============================================================================
// Batch Pure White Background Filler for Adobe Photoshop (ExtendScript)
// Part of Phase 01: Dataset Curation & Cleanup (Pony XL Branch)
// ============================================================================

// --- SILENT MODE ---
app.displayDialogs = DialogModes.NO;

// --- WORKING DIRECTORIES ---
var origenDir = new Folder("./input/DataSetPONY/sinFondo");
var destinoDir = new Folder("./input/DataSetPONY/fondoBlanco");

if (!destinoDir.exists) {
    destinoDir.create();
}

// Scan all transparent PNG cutouts
var archivos = origenDir.getFiles(/\.(jpg|jpeg|png|webp)$/i);
var totalProcesados = 0;

for (var i = 0; i < archivos.length; i++) {
    var archivoActual = archivos[i];

    // Format output filename
    var nombreLimpio = archivoActual.name.substring(0, archivoActual.name.lastIndexOf("."));
    var rutaFinal = destinoDir.fsName + "/" + nombreLimpio + ".png";
    var archivoDestino = new File(rutaFinal);

    // Skip if already processed (idempotent execution)
    if (archivoDestino.exists) continue;

    try {
        // 1. Open transparent cutout
        var doc = app.open(archivoActual);

        // 2. Enforce native RGB color mode
        if (doc.mode != DocumentMode.RGB) {
            doc.changeMode(ChangeMode.RGB);
        }

        // 3. Create solid background layer behind subject
        var capaFondoBlanco = doc.artLayers.add();
        capaFondoBlanco.name = "Pure_White_Background";
        capaFondoBlanco.move(doc.layers[doc.layers.length - 1], ElementPlacement.PLACEAFTER);

        // 4. Fill with pure studio white (#FFFFFF)
        var colorBlanco = new SolidColor();
        colorBlanco.rgb.red = 255;
        colorBlanco.rgb.green = 255;
        colorBlanco.rgb.blue = 255;

        doc.selection.selectAll();
        doc.selection.fill(colorBlanco);
        doc.selection.deselect();

        // 5. Flatten layers into a single lossless PNG
        doc.flatten();

        var opcionesPng = new PNGSaveOptions();
        opcionesPng.compression = 5;
        opcionesPng.interlaced = false;
        doc.saveAs(archivoDestino, opcionesPng, true, Extension.LOWERCASE);

        // 6. Close document & purge memory
        doc.close(SaveOptions.DONOTSAVECHANGES);
        app.purge(PurgeTarget.HISTORY);
        app.purge(PurgeTarget.CLIPBOARD);
        totalProcesados++;

    } catch (error) {
        try {
            app.activeDocument.close(SaveOptions.DONOTSAVECHANGES);
            app.purge(PurgeTarget.ALLPURGES);
        } catch (e) {}
    }
}

// Restore Photoshop dialogs
app.displayDialogs = DialogModes.ALL;

alert("PROCESS COMPLETE!\n\nImages with pure white background saved (" + totalProcesados + ") to:\n" + destinoDir.fsName);