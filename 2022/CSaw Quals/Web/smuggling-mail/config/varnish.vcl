vcl 4.1;

backend default {
    .host = "127.0.0.1:8082";
}

sub vcl_recv {
    if (req.url ~ "/admin" && !(req.http.Authorization ~ "^Basic esun5Fjrk2NACwy_WuZl8UIJAQfQzXBJWC3cxw0ZduwZzgt-rBs5fq6xytrBNB0E$")) {
        return (synth(403, "Access Denied"));
    }
}

sub vcl_synth {
    if (resp.status == 403) {
        set resp.body = resp.reason;
        return (deliver);
    }
}
