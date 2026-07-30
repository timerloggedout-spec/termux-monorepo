use scraper::Html;
use ego_tree::NodeRef;
use std::collections::HashMap;

fn tag_to_token(tag: &str) -> Option<String> {
    let m = HashMap::from([
        ("a", "@"),
        ("img", "%"),
        ("table", "^"),
        ("td", "`"),
        ("tr", "|"),
        ("div", ";"),
        ("span", ":"),
        ("script", "{"),
        ("style", "["),
        ("input", "?"),
        ("form", "?="),
        ("ul", "("),
        ("li", "-"),
        ("h1", "#"),
        ("em", "*"),
        ("i", "_"),
        ("blockquote", ">"),
        ("section", "!"),
        ("aside", "$"),
        ("link", "&"),
        ("button", "+"),
        ("textarea", "~"),
        ("label", "'"),
        ("p", "p"),
        ("br", "/"),
    ]);
    m.get(tag).map(|s| s.to_string())
}


pub fn reverse_compile(html: &str) -> String {
    let document = Html::parse_document(html);
    let mut out = String::new();
    // Walk the root element's children
    for child in document.root_element().children() {
        emit_node(&child, 0, &mut out);
    }
    out
}

fn emit_node(node: &NodeRef<scraper::Node>, indent: usize, out: &mut String) {
    if let Some(el) = node.value().as_element() {
        let tag_name = el.name();
        let token = tag_to_token(tag_name).unwrap_or_else(|| tag_name.to_string());

        let mut attr_str = String::new();
        for (k, v) in el.attrs() {
            match k {
                "class" => attr_str.push_str(&format!(".{}", v.replace(' ', "."))),
                "id" => attr_str.push_str(&format!("#{}", v)),
                _ => attr_str.push_str(&format!(" {}=\"{}\"", k, v)),
            }
        }

        let children: Vec<_> = node.children().collect();
        let has_elem = children.iter().any(|c| c.value().as_element().is_some());
        let text_concat: String = children
            .iter()
            .filter_map(|c| c.value().as_text().map(|t| t.trim().to_string()))
            .collect::<Vec<_>>()
            .join(" ");

        let void_elems = ["br","hr","img","input","link","meta","area","base","col","embed","source","track","wbr"];
        if void_elems.contains(&tag_name) {
            push_line(out, indent, &format!("{}{}/", token, attr_str));
        } else if children.is_empty() {
            push_line(out, indent, &format!("{}{}", token, attr_str));
        } else if !has_elem && !text_concat.is_empty() {
            push_line(out, indent, &format!("{} \"{}\"", token, text_concat));
        } else {
            push_line(out, indent, &format!("{}{}", token, attr_str));
            for child in children {
                emit_node(&child, indent + 2, out);
            }
        }
    } else if let Some(t) = node.value().as_text() {
        let text = t.trim().to_string();
        if !text.is_empty() {
            push_line(out, indent, &text);
        }
    }
}
fn push_line(out: &mut String, indent: usize, content: &str) {
    out.push_str(&" ".repeat(indent));
    out.push_str(content);
    out.push('\n');
}
