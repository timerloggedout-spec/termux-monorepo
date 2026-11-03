package org.timerloggedout.studysprint;

import android.app.Activity;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
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
 *
 * Build D (issue #4242): the web bundle's ingest legs use HTML
 * file inputs (a text picker + a camera-capture input with
 * accept="image/*" capture="environment"). A stock WebView
 * silently ignores file inputs, so the shell wires
 * WebChromeClient.onShowFileChooser to the system chooser and
 * returns the picked/captured URIs to the page — the capture /
 * picker wiring for this surface.
 */
public class MainActivity extends Activity {

    private static final int FILE_CHOOSER_REQUEST = 4242;

    private WebView webView;
    private ValueCallback<Uri[]> filePathCallback;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        webView = new WebView(this);
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        webView.setWebViewClient(new WebViewClient());
        webView.setWebChromeClient(new WebChromeClient() {
            @Override
            public boolean onShowFileChooser(
                    WebView view,
                    ValueCallback<Uri[]> callback,
                    FileChooserParams params) {
                if (filePathCallback != null) {
                    filePathCallback.onReceiveValue(null);
                }
                filePathCallback = callback;
                Intent intent = params.createIntent();
                try {
                    startActivityForResult(intent,
                                           FILE_CHOOSER_REQUEST);
                } catch (Exception e) {
                    filePathCallback = null;
                    return false;
                }
                return true;
            }
        });
        setContentView(webView);
        webView.loadUrl("file:///android_asset/web/index.html");
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode,
                                    Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode != FILE_CHOOSER_REQUEST
                || filePathCallback == null) {
            return;
        }
        Uri[] results = null;
        if (resultCode == RESULT_OK && data != null) {
            results = WebChromeClient.FileChooserParams
                    .parseResult(resultCode, data);
        }
        filePathCallback.onReceiveValue(results);
        filePathCallback = null;
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
