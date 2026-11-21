package com.timerloggedout.fleet;

// [MUSEai]@{role:{apk-release}} :: programmatic UI only (∅ R class, ∅ resources ⇒ aapt2 link stays trivial)

import android.app.Activity;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.Bundle;
import android.widget.TextView;

public class MainActivity extends Activity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        String versionName = "unknown";
        long versionCode = -1;
        try {
            PackageInfo pInfo = getPackageManager().getPackageInfo(getPackageName(), 0);
            versionName = pInfo.versionName;
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
                versionCode = pInfo.getLongVersionCode();
            } else {
                versionCode = pInfo.versionCode;
            }
        } catch (PackageManager.NameNotFoundException e) {
            // keep default fallback values
        }

        int sdkInt = Build.VERSION.SDK_INT;

        TextView view = new TextView(this);
        String text = "termux-monorepo fleet .APK\n"
                + "package: com.timerloggedout.fleet\n"
                + "versionName: " + versionName + "\n"
                + "versionCode: " + versionCode + "\n"
                + "device SDK: " + sdkInt + "\n"
                + "lane: apk-release (docs/ops/APK-RELEASE-LANE.md)";
        view.setText(text);
        view.setPadding(48, 48, 48, 48);
        view.setTextSize(16);
        setContentView(view);
    }
}
