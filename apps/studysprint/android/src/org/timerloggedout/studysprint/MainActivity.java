package org.timerloggedout.studysprint;

import android.app.Activity;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import java.io.IOException;
import java.io.InputStream;
import java.util.HashMap;
import java.util.Map;

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
 * returns the picked/captured URIs to the page -- the capture /
 * picker wiring for this surface.
 *
 * Device-smoke fix (evidence/apk/SMOKE.md, 2026-11-03): the
 * bundle's fetch("data/state.json") never completed inside the
 * WebView -- a page loaded from a file:/// origin may not fetch
 * sibling files under the WebView's file-origin rules, so every
 * view sat at "Loading your course..." with an empty version
 * footer (the same bundle rendered fully in mobile Chrome). The
 * shell's WebViewClient now intercepts requests under its own
 * /android_asset/web/ path and serves them from the APK assets
 * with an Access-Control-Allow-Origin header -- the
 * dependency-free equivalent of serving the bundle over a local
 * origin. Interception is scoped to the app's own asset path;
 * everything else falls through untouched.
 *
 * https-origin serving (issue #4412, follow-up via the #4283
 * emulator gate): the interception above was NOT sufficient in
 * the AOSP emulator's older WebView -- the gate's master run
 * rendered the named load-failure state, because an intercepted
 * fetch from a file:// page is still blocked at the fetch layer
 * in that WebView generation despite the CORS header (the 0.1.0
 * repro and every ruled-out alternative are stamped on #4283).
 * The bundle is therefore now loaded from the reserved https
 * origin https://appassets.androidplatform.net/assets/... --
 * the WebViewAssetLoader pattern: page and fetch share one
 * secure https origin, no CORS, no file-origin rules. The build
 * is SDK-direct (javac against android.jar, no dependency
 * resolver) and androidx.webkit is not in android.jar, so the
 * pattern is implemented with framework APIs only -- a
 * shouldInterceptRequest handler for the reserved domain, which
 * is exactly what WebViewAssetLoader does internally. The legacy
 * /android_asset/ interception stays as a fallback for any
 * file:// navigation; interception remains scoped to the app's
 * own web/ assets on both paths.
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
        webView.setWebViewClient(new WebViewClient() {
            @Override
            public WebResourceResponse shouldInterceptRequest(
                    WebView view, WebResourceRequest request) {
                Uri url = request.getUrl();
                String path = url.getPath();
                if (path == null) {
                    return null;
                }
                // WebViewAssetLoader pattern (#4412): the reserved
                // https domain's /assets/ tree maps onto the APK
                // assets root, so /assets/web/... serves the same
                // bytes the legacy branch below serves -- under a
                // secure origin the fetch layer accepts everywhere.
                if ("appassets.androidplatform.net".equals(
                        url.getHost())
                        && path.startsWith("/assets/")) {
                    return serve(path.substring("/assets/".length()));
                }
                String prefix = "/android_asset/";
                if (!path.startsWith(prefix)) {
                    return null;
                }
                return serve(path.substring(prefix.length()));
            }

            private WebResourceResponse serve(String asset) {
                if (!asset.startsWith("web/")) {
                    return null;
                }
                try {
                    InputStream in = getAssets().open(asset);
                    Map<String, String> headers = new HashMap<>();
                    headers.put("Access-Control-Allow-Origin", "*");
                    return new WebResourceResponse(mimeFor(asset),
                            "utf-8", 200, "OK", headers, in);
                } catch (IOException e) {
                    return null;
                }
            }

            private String mimeFor(String asset) {
                if (asset.endsWith(".html")) return "text/html";
                if (asset.endsWith(".js")) return "text/javascript";
                if (asset.endsWith(".css")) return "text/css";
                if (asset.endsWith(".json")) return "application/json";
                if (asset.endsWith(".webmanifest")) {
                    return "application/manifest+json";
                }
                if (asset.endsWith(".png")) return "image/png";
                if (asset.endsWith(".svg")) return "image/svg+xml";
                return "application/octet-stream";
            }
        });
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
        webView.loadUrl(
            "https://appassets.androidplatform.net/assets/web/index.html");
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
