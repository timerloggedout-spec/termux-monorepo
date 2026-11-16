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
            let children_html = join_children(children);
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

fn join_children(children: &[ASTNode]) -> String {
    let mut result = String::new();
    let mut prev_was_text = false;
    for child in children {
        match child {
            ASTNode::Text(t) => {
                if prev_was_text {
                    result.push(' ');
                }
                result.push_str(t);
                prev_was_text = true;
            }
            _ => {
                result.push_str(&emit_html(child));
                prev_was_text = false;
            }
        }
    }
    result
}

fn is_void(tag: &str) -> bool {
    matches!(tag, "br" | "img" | "input" | "hr")
}
