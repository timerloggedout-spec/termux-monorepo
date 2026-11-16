#!/usr/bin/env python3
main_rs = r##"use logos::Logos;

#[derive(Logos, Debug, PartialEq, Clone)]
#[allow(dead_code)]
enum Token {
    #[regex("@", priority = 1)] Anchor,
    #[regex("%", priority = 1)] Image,
    #[regex(r"\^", priority = 1)] Table,
    #[regex("`", priority = 1)] TableCell,
    #[regex("=", priority = 1)] TableRow,
    #[regex("/", priority = 1)] LineBreak,
    #[regex(";", priority = 1)] Div,
    #[regex(":", priority = 1)] Span,
    #[token("{")] ScriptOpen,
    #[token("[")] StyleOpen,
    #[regex(r"\?", priority = 1)] Input,
    #[token("?=")] Form,
    #[regex(r"\(", priority = 1)] UnorderedList,
    #[regex("-", priority = 1)] ListItem,
    #[regex("#", priority = 1)] Heading,
    #[regex(r"\*", priority = 1)] Em,
    #[regex("_", priority = 1)] Italic,
    #[regex(">", priority = 1)] Blockquote,
    #[regex("!", priority = 1)] Section,
    #[regex(r"\$", priority = 1)] Aside,
    #[regex("&", priority = 1)] Link,
    #[regex(r"\+", priority = 1)] Button,
    #[regex("~", priority = 1)] TextArea,
    #[regex("'", priority = 1)] Label,
    #[regex("p", priority = 1)] Paragraph,
    #[regex("S", priority = 1)] Svg,
    #[regex("P", priority = 1)] Path,
    #[regex("R", priority = 1)] Rect,
    #[regex("C", priority = 1)] Circle,
    #[regex("E", priority = 1)] Ellipse,
    #[regex("L", priority = 1)] Line,
    #[regex("Y", priority = 1)] Polyline,
    #[regex("G", priority = 1)] Group,
    #[regex("D", priority = 1)] Defs,
    #[regex("T", priority = 1)] Text,
    #[regex("I", priority = 1)] SvgImage,
    #[regex("U", priority = 1)] Use,
    #[token("LG")] LinearGradient,
    #[token("RG")] RadialGradient,
    #[token("ST")] Stop,
    #[token("TS")] Tspan,
    #[token("TP")] TextPath,
    #[token("YS")] Symbol,
    #[token("CP")] ClipPath,
    #[token("{%")] LogicOpen,
    #[token("%}")] LogicClose,
    #[token("{{")] InterpolationOpen,
    #[token("}}")] InterpolationClose,
    #[token(":::")] Fence,
    #[regex(r"\.[a-zA-Z_-][a-zA-Z0-9_-]*", |lex| lex.slice().to_string())] Class(String),
    #[regex(r"[a-zA-Z_-][a-zA-Z0-9_-]*=", |lex| lex.slice().trim_end_matches('=').to_string())] AttrName(String),
    #[regex(r#"[^"]*""#, |lex| lex.slice().to_string())] QuotedValue(String),
    #[regex(r"[a-zA-Z_][a-zA-Z0-9_-]*", |lex| lex.slice().to_string())] Ident(String),
    #[token("\n")] Newline,
    #[regex(r"[ \t]+", |lex| lex.slice().to_string())] Whitespace(String),
    #[regex(".", priority = 0)] Unknown,
}

#[derive(Debug)]
enum ASTNode {
    Element {
        tag: String,
        classes: Vec<String>,
        attrs: Vec<(String, String)>,
        children: Vec<ASTNode>,
    },
    Text(String),
}

fn parse(tokens: Vec<Token>, _source: &str) -> Vec<ASTNode> {
    let mut nodes = Vec::new();
    let mut i = 0;
    let len = tokens.len();
    while i < len {
        if matches!(tokens[i], Token::Newline) {
            i += 1;
            continue;
        }
        let (node, next) = parse_node(&tokens, i);
        nodes.push(node);
        i = next;
    }
    nodes
}

fn parse_node(tokens: &[Token], start: usize) -> (ASTNode, usize) {
    let token = &tokens[start];
    match token {
        Token::Div | Token::Span | Token::Button | Token::Section | Token::Aside |
        Token::Paragraph | Token::Heading | Token::UnorderedList | Token::ListItem |
        Token::Blockquote | Token::Svg | Token::Path | Token::Rect | Token::Circle |
        Token::Ellipse | Token::Line | Token::Polyline | Token::Group | Token::Defs |
        Token::Text | Token::SvgImage | Token::Use | Token::Anchor | Token::Image |
        Token::Table | Token::TableCell | Token::TableRow | Token::Form | Token::Input |
        Token::TextArea | Token::Label => {
            let tag = match token {
                Token::Div => "div",
                Token::Span => "span",
                Token::Button => "button",
                Token::Section => "section",
                Token::Aside => "aside",
                Token::Paragraph => "p",
                Token::Heading => "h1",
                Token::UnorderedList => "ul",
                Token::ListItem => "li",
                Token::Blockquote => "blockquote",
                Token::Svg => "svg",
                Token::Path => "path",
                Token::Rect => "rect",
                Token::Circle => "circle",
                Token::Ellipse => "ellipse",
                Token::Line => "line",
                Token::Polyline => "polyline",
                Token::Group => "g",
                Token::Defs => "defs",
                Token::Text => "text",
                Token::SvgImage => "image",
                Token::Use => "use",
                Token::Anchor => "a",
                Token::Image => "img",
                Token::Table => "table",
                Token::TableCell => "td",
                Token::TableRow => "tr",
                Token::Form => "form",
                Token::Input => "input",
                Token::TextArea => "textarea",
                Token::Label => "label",
                _ => unreachable!(),
            };
            let mut i = start + 1;
            let mut classes = Vec::new();
            let mut attrs = Vec::new();
            while i < tokens.len() {
                match &tokens[i] {
                    Token::Class(c) => {
                        classes.push(c.clone());
                        i += 1;
                    }
                    Token::AttrName(name) => {
                        let name = name.clone();
                        i += 1;
                        if i < tokens.len() {
                            if let Token::QuotedValue(val) = &tokens[i] {
                                attrs.push((name, val.clone()));
                                i += 1;
                            } else if let Token::Ident(val) = &tokens[i] {
                                attrs.push((name, val.clone()));
                                i += 1;
                            }
                        }
                    }
                    Token::Newline => {
                        i += 1;
                        break;
                    }
                    _ => break,
                }
            }
            let mut children = Vec::new();
            if i < tokens.len() && matches!(tokens[i], Token::Newline) {
                let mut peek = i + 1;
                let mut child_indent = 0;
                if peek < tokens.len() {
                    if let Token::Whitespace(ws) = &tokens[peek] {
                        child_indent = ws.len();
                        peek += 1;
                    }
                }
                if child_indent > 0 {
                    i = peek;
                    while i < tokens.len() {
                        if matches!(tokens[i], Token::Newline) {
                            i += 1;
                            if i < tokens.len() {
                                if let Token::Whitespace(ws) = &tokens[i] {
                                    if ws.len() < child_indent {
                                        break;
                                    }
                                    i += 1;
                                } else {
                                    break;
                                }
                            }
                            continue;
                        }
                        let (child, next) = parse_node(tokens, i);
                        children.push(child);
                        i = next;
                    }
                }
            }
            (ASTNode::Element {
                tag: tag.to_string(),
                classes,
                attrs,
                children,
            }, i)
        }
        Token::Ident(text) => {
            (ASTNode::Text(text.clone()), start + 1)
        }
        Token::InterpolationOpen => {
            let mut content = String::new();
            let mut i = start + 1;
            while i < tokens.len() {
                match &tokens[i] {
                    Token::InterpolationClose => {
                        i += 1;
                        break;
                    }
                    Token::Ident(s) | Token::Class(s) => {
                        content.push_str(s);
                        i += 1;
                    }
                    _ => {
                        content.push_str(&format!("{:?}", tokens[i]));
                        i += 1;
                    }
                }
            }
            (ASTNode::Text(format!("{{{{{}}}}}", content)), i)
        }
        _ => {
            (ASTNode::Text(format!("<unknown: {:?}>", token)), start + 1)
        }
    }
}

fn main() {
    let source = r#";
; .container
  p {{ title }}
  + on:click="increment" "Click me"
"#;
    let lex = Token::lexer(source);
    let tokens: Vec<Token> = lex.collect();
    println!("Tokens: {:?}", tokens);
    let ast = parse(tokens, source);
    println!("AST: {:#?}", ast);
}
"##
with open("src/main.rs", "w") as f:
    f.write(main_rs)
print("OK")
