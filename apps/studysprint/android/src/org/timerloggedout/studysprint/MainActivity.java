package org.timerloggedout.studysprint;

import android.app.Activity;
import android.os.Bundle;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

/**
 * StudySprint APK surface (issue #4093).
 *
 * A thin native shell: the WebView renders the webApp bundle
 * (apps/studysprint/web) bundled into the APK assets at build time,
 * with the core-generated state (data/state.json) inside it. SR
 * review state persists on-device in the WebView's localStorage.
 * No network: everything the surface needs ships in the .apk.
 */
public class MainActivity extends Activity {

    private WebView webView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        webView = new WebView(this);
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        webView.setWebViewClient(new WebViewClient());
        setContentView(webView);
        webView.loadUrl("file:///android_asset/web/index.html");
    }

    @Override
    public void onBackPressed() {
        if (webView != null && webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }
}
