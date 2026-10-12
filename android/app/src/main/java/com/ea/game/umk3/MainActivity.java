package com.ea.game.umk3;

import org.libsdl.app.SDLActivity;
import android.os.Bundle;
import android.util.Log;
import java.io.*;
import java.util.Enumeration;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;

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
        if (probeFile.exists() && probeFile.length() > 0) {
            Log.i(TAG, "Assets already extracted to " + internalRes.getAbsolutePath());
            return;
        }

        internalRes.mkdirs();
        try {
            Log.i(TAG, "Extracting assets from APK to internal storage...");
            boolean extractedViaZip = false;
            try {
                ZipFile zip = new ZipFile(new File(getPackageCodePath()));
                Enumeration<? extends ZipEntry> entries = zip.entries();
                byte[] buffer = new byte[32768];

                while (entries.hasMoreElements()) {
                    ZipEntry entry = entries.nextElement();
                    String name = entry.getName();

                    if (name.startsWith("assets/res/")) {
                        String relPath = name.substring("assets/res/".length());
                        if (relPath.isEmpty()) continue;
                        File outFile = new File(internalRes, relPath);
                        if (entry.isDirectory()) {
                            outFile.mkdirs();
                        } else {
                            File parent = outFile.getParentFile();
                            if (parent != null && !parent.exists()) parent.mkdirs();
                            try (InputStream in = zip.getInputStream(entry);
                                 OutputStream out = new FileOutputStream(outFile)) {
                                int len;
                                while ((len = in.read(buffer)) > 0) {
                                    out.write(buffer, 0, len);
                                }
                            }
                        }
                    } else if (name.equals("assets/Info.plist")) {
                        File outFile1 = new File(internalRes, "Info.plist");
                        File outFile2 = new File(getFilesDir(), "Info.plist");
                        try (InputStream in = zip.getInputStream(entry)) {
                            ByteArrayOutputStream baos = new ByteArrayOutputStream();
                            int len;
                            while ((len = in.read(buffer)) > 0) {
                                baos.write(buffer, 0, len);
                            }
                            byte[] plistBytes = baos.toByteArray();
                            try (FileOutputStream fos1 = new FileOutputStream(outFile1)) {
                                fos1.write(plistBytes);
                            }
                            try (FileOutputStream fos2 = new FileOutputStream(outFile2)) {
                                fos2.write(plistBytes);
                            }
                        }
                    }
                }
                zip.close();
                extractedViaZip = true;
            } catch (Exception ze) {
                Log.w(TAG, "Fast zip extract failed, falling back to AssetManager: " + ze.getMessage());
            }

            if (!extractedViaZip || !probeFile.exists()) {
                copyAssetFolder(getAssets(), "res", internalRes);
                copyAssetFile(getAssets(), "Info.plist", new File(internalRes, "Info.plist"));
                copyAssetFile(getAssets(), "Info.plist", new File(getFilesDir(), "Info.plist"));
            }

            Log.i(TAG, "Assets extracted successfully!");
        } catch (Exception e) {
            Log.e(TAG, "Failed extracting assets: " + e.getMessage(), e);
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
