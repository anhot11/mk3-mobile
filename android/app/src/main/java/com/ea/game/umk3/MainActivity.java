package com.ea.game.umk3;

import org.libsdl.app.SDLActivity;
import android.os.Bundle;
import android.os.Build;
import android.os.Vibrator;
import android.os.VibrationEffect;
import android.content.Context;
import android.content.SharedPreferences;
import android.media.AudioManager;
import android.view.View;
import android.view.WindowManager;
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
        // Enable edge-to-edge drawing into display cutout (notch)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
            getWindow().getAttributes().layoutInDisplayCutoutMode =
                WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_SHORT_EDGES;
        }

        setVolumeControlStream(AudioManager.STREAM_MUSIC);
        copyAssetsToInternalStorage();
        super.onCreate(savedInstanceState);
        hideSystemUI();
    }

    @Override
    public void onWindowFocusChanged(boolean hasFocus) {
        super.onWindowFocusChanged(hasFocus);
        if (hasFocus) {
            hideSystemUI();
        }
    }

    private void hideSystemUI() {
        View decorView = getWindow().getDecorView();
        decorView.setSystemUiVisibility(
            View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
            | View.SYSTEM_UI_FLAG_LAYOUT_STABLE
            | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
            | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
            | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
            | View.SYSTEM_UI_FLAG_FULLSCREEN);
    }

    public static void vibrate(int milliseconds) {
        if (getContext() != null) {
            try {
                Vibrator v = (Vibrator) getContext().getSystemService(Context.VIBRATOR_SERVICE);
                if (v != null && v.hasVibrator()) {
                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                        v.vibrate(VibrationEffect.createOneShot(milliseconds, VibrationEffect.DEFAULT_AMPLITUDE));
                    } else {
                        v.vibrate(milliseconds);
                    }
                    Log.d(TAG, "Vibrated for " + milliseconds + "ms");
                }
            } catch (Exception e) {
                Log.e(TAG, "Vibrate error: " + e.getMessage());
            }
        }
    }

    private void copyAssetsToInternalStorage() {
        SharedPreferences prefs = getSharedPreferences("umk3_prefs", MODE_PRIVATE);
        int lastExtractedVersion = prefs.getInt("extracted_version", -1);
        int currentVersion = 2;
        try {
            currentVersion = getPackageManager().getPackageInfo(getPackageName(), 0).versionCode;
        } catch (Exception ignored) {}

        File internalRes = new File(getFilesDir(), "res");
        File probeFile = new File(internalRes, "Info.plist");
        if (lastExtractedVersion == currentVersion && probeFile.exists() && probeFile.length() > 0) {
            Log.i(TAG, "Assets already up-to-date for version " + currentVersion);
            return;
        }

        internalRes.mkdirs();
        try {
            Log.i(TAG, "Extracting assets from APK to internal storage (version " + currentVersion + ")...");
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

            prefs.edit().putInt("extracted_version", currentVersion).apply();
            Log.i(TAG, "Assets extracted successfully for version " + currentVersion + "!");
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
