package com.timerloggedout.fleet;

// [MUSEai]@{role:{apk-release}} :: programmatic UI only (∅ R class, ∅ resources ⇒ aapt2 link stays trivial)

import android.app.Activity;
import android.os.Bundle;
import android.widget.TextView;

public class MainActivity extends Activity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        TextView view = new TextView(this);
        view.setText("termux-monorepo fleet .APK\npackage: com.timerloggedout.fleet\nlane: apk-release (docs/ops/APK-RELEASE-LANE.md)");
        view.setPadding(48, 48, 48, 48);
        view.setTextSize(16);
        setContentView(view);
    }
}
