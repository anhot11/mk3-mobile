package com.ea.game.umk3;

import org.libsdl.app.SDLActivity;
import android.os.Bundle;
import android.util.Log;
import java.io.*;

public class MainActivity extends SDLActivity {
    private static final String TAG = "UMK3";

    @Override
    protected String[] getLibraries() {
        return new String[] {
            "SDL2",
            "main"
        };
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        copyAssetsToInternalStorage();
        super.onCreate(savedInstanceState);
    }

    private void copyAssetsToInternalStorage() {
        File internalRes = new File(getFilesDir(), "res");
        File probeFile = new File(internalRes, "Info.plist");
        if (probeFile.exists()) {
            Log.i(TAG, "Assets already extracted to " + internalRes.getAbsolutePath());
            return;
        }

        internalRes.mkdirs();
        try {
            Log.i(TAG, "Copying assets to internal storage...");
            copyAssetFolder(getAssets(), "res", internalRes);
            copyAssetFile(getAssets(), "Info.plist", new File(getFilesDir(), "Info.plist"));
            Log.i(TAG, "Assets copied successfully!");
        } catch (Exception e) {
            Log.e(TAG, "Failed copying assets: " + e.getMessage(), e);
        }
    }

    private void copyAssetFolder(android.content.res.AssetManager assetManager, String fromAssetPath, File toDir) throws IOException {
        String[] files = assetManager.list(fromAssetPath);
        if (files == null || files.length == 0) {
            copyAssetFile(assetManager, fromAssetPath, toDir);
        } else {
            if (!toDir.exists()) toDir.mkdirs();
            for (String file : files) {
                String subPath = fromAssetPath.isEmpty() ? file : fromAssetPath + "/" + file;
                File target = new File(toDir, file);
                copyAssetFolder(assetManager, subPath, target);
            }
        }
    }

    private void copyAssetFile(android.content.res.AssetManager assetManager, String fromAssetPath, File toFile) throws IOException {
        if (toFile.exists() && toFile.length() > 0) return;
        File parent = toFile.getParentFile();
        if (parent != null && !parent.exists()) parent.mkdirs();
        try (InputStream in = assetManager.open(fromAssetPath);
             OutputStream out = new FileOutputStream(toFile)) {
            byte[] buffer = new byte[16384];
            int read;
            while ((read = in.read(buffer)) != -1) {
                out.write(buffer, 0, read);
            }
        }
    }
}
