use crate::parser::ASTNode;

pub fn emit_html(node: &ASTNode) -> String {
    match node {
        ASTNode::Element {
            tag,
            classes,
            attrs,
            children,
        } => {
            let class_str = if classes.is_empty() {
                String::new()
            } else {
                format!(" class=\"{}\"", classes.join(" "))
            };
            let attrs_str = attrs
                .iter()
                .map(|(k, v)| format!(" {}=\"{}\"", k, v))
                .collect::<Vec<_>>()
                .join("");
            let children_html = children.iter().map(emit_html).collect::<Vec<_>>().join("");
            if is_void(tag) {
                format!("<{}{}{}/>", tag, class_str, attrs_str)
            } else {
                format!(
                    "<{}{}{}>{}</{}>",
                    tag, class_str, attrs_str, children_html, tag
                )
            }
        }
        ASTNode::Text(text) => text.clone(),
    }
}

fn is_void(tag: &str) -> bool {
    matches!(tag, "br" | "img" | "input" | "hr")
}
