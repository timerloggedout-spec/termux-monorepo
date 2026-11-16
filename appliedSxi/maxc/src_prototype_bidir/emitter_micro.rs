use crate::parser::ASTNode;

fn encode_leb128(mut value: u32) -> Vec<u8> {
    let mut bytes = vec![];
    loop {
        let mut byte = (value & 0x7F) as u8;
        value >>= 7;
        if value != 0 { byte |= 0x80; }
        bytes.push(byte);
        if value == 0 { break; }
    }
    bytes
}

fn token_id(tok: &str) -> u8 {
    match tok {
        ";"|"div" => 0x00, ":"|"span" => 0x01, "p" => 0x02,
        "@"|"a" => 0x03, "%"|"img" => 0x04, "+"|"button" => 0x05,
        "?"|"input" => 0x06, "?="|"form" => 0x07, "("|"ul" => 0x08,
        "-"|"li" => 0x09, "#"|"h1" => 0x0A, "*"|"em" => 0x0B,
        "_"|"i" => 0x0C, ">"|"blockquote" => 0x0D, "!"|"section" => 0x0E,
        "$"|"aside" => 0x0F, "&"|"link" => 0x10, "~"|"textarea" => 0x11,
        "'"|"label" => 0x12, "/"|"br" => 0x13, "hr" => 0x14,
        "^"|"table" => 0x15, "|"|"tr" => 0x16, "`"|"td" => 0x17,
        "{"|"script" => 0x18, "["|"style" => 0x19, "S"|"svg" => 0x1A,
        "P"|"path" => 0x1B, "R"|"rect" => 0x1C, "C"|"circle" => 0x1D,
        "E"|"ellipse" => 0x1E, "L"|"line" => 0x1F, "Y"|"polyline" => 0x20,
        "G"|"g" => 0x21, "D"|"defs" => 0x22, "T"|"text" => 0x23,
        "I"|"image" => 0x24, "U"|"use" => 0x25,
        _ => 0xFF,
    }
}

pub fn emit_micro(ast: &[ASTNode]) -> Vec<u8> {
    let mut buf = vec![];
    buf.extend_from_slice(b"MAXC");
    buf.push(0x01); // version
    for node in ast {
        serialize_node(node, &mut buf);
    }
    buf
}

fn serialize_node(node: &ASTNode, buf: &mut Vec<u8>) {
    match node {
        ASTNode::Element { tag, attrs, children, .. } => {
            buf.push(0x01);
            buf.push(token_id(tag));

            // Flags: id/class shortcuts
            let has_id = attrs.iter().any(|(k,_)| k == "id");
            let has_class = attrs.iter().any(|(k,_)| k == "class");
            let flags = (if has_id { 0x01 } else { 0 })
                      | (if has_class { 0x02 } else { 0 });
            buf.push(flags);

            let attr_count = attrs.len();
            buf.extend(&encode_leb128(attr_count as u32));
            for (key, value) in attrs {
                if (has_id && key == "id") || (has_class && key == "class") {
                    // Omit key, write length 0
                    buf.push(0);
                } else {
                    let key_bytes = key.as_bytes();
                    buf.extend(&encode_leb128(key_bytes.len() as u32));
                    buf.extend_from_slice(key_bytes);
                }
                let val_bytes = value.as_bytes();
                buf.extend(&encode_leb128(val_bytes.len() as u32));
                buf.extend_from_slice(val_bytes);
            }

            let child_count = children.len();
            buf.extend(&encode_leb128(child_count as u32));
            for child in children {
                serialize_node(child, buf);
            }
        }
        ASTNode::Text(text) => {
            buf.push(0x02);
            let bytes = text.as_bytes();
            buf.extend(&encode_leb128(bytes.len() as u32));
            buf.extend_from_slice(bytes);
        }
    }
}
