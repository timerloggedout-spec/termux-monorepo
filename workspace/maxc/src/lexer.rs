use logos::Logos;

#[derive(Logos, Debug, PartialEq, Clone)]
#[allow(dead_code)]
pub enum Token {
    #[regex("@", priority = 4)]
    Anchor,
    #[regex("%", priority = 4)]
    Image,
    #[regex("\\^", priority = 4)]
    Table,
    #[regex("`", priority = 4)]
    TableCell,
    #[regex("\\|", priority = 4)]
    TableRow,
    #[regex("=", priority = 4)]
    Equals,
    #[regex("/", priority = 4)]
    LineBreak,
    #[regex(";", priority = 4)]
    Div,
    #[regex(":", priority = 4)]
    Span,
    #[token("{")]
    ScriptOpen,
    #[token("[")]
    StyleOpen,
    #[regex("\\?", priority = 4)]
    Input,
    #[token("?=")]
    Form,
    #[regex("\\(", priority = 4)]
    UnorderedList,
    #[regex("-", priority = 4)]
    ListItem,
    #[regex("#", priority = 4)]
    Heading,
    #[regex("\\*", priority = 4)]
    Em,
    #[regex("_", priority = 4)]
    Italic,
    #[regex(">", priority = 4)]
    Blockquote,
    #[regex("!", priority = 4)]
    Section,
    #[regex("\\$", priority = 4)]
    Aside,
    #[regex("&", priority = 4)]
    Link,
    #[regex("\\+", priority = 4)]
    Button,
    #[regex("~", priority = 4)]
    TextArea,
    #[regex("'", priority = 4)]
    Label,
    #[regex("p", priority = 4)]
    Paragraph,
    #[regex("S", priority = 4)]
    Svg,
    #[regex("P", priority = 4)]
    Path,
    #[regex("R", priority = 4)]
    Rect,
    #[regex("C", priority = 4)]
    Circle,
    #[regex("E", priority = 4)]
    Ellipse,
    #[regex("L", priority = 4)]
    Line,
    #[regex("Y", priority = 4)]
    Polyline,
    #[regex("G", priority = 4)]
    Group,
    #[regex("D", priority = 4)]
    Defs,
    #[regex("T", priority = 4)]
    Text,
    #[regex("I", priority = 4)]
    SvgImage,
    #[regex("U", priority = 4)]
    Use,
    #[token("LG")]
    LinearGradient,
    #[token("RG")]
    RadialGradient,
    #[token("ST")]
    Stop,
    #[token("TS")]
    Tspan,
    #[token("TP")]
    TextPath,
    #[token("YS")]
    Symbol,
    #[token("CP")]
    ClipPath,
    #[token("{%")]
    LogicOpen,
    #[token("%}")]
    LogicClose,
    #[token("{{")]
    InterpolationOpen,
    #[token("}}")]
    InterpolationClose,
    #[token(":::")]
    Fence,
    #[token("\n")]
    Newline,

    #[regex(r"[a-zA-Z_][a-zA-Z0-9_-]*(:[a-zA-Z_][a-zA-Z0-9_-]*)*",
        |lex| lex.slice().to_string(), priority = 3)]
    AttrName(String),
    #[regex(r#"=\"[^\"]*\""#,
        |lex| lex.slice()[2..lex.slice().len()-1].to_string(), priority = 2)]
    QuotedValue(String),
    #[regex(r"\.[a-zA-Z_-][a-zA-Z0-9_-]*",
        |lex| lex.slice()[1..].to_string(), priority = 2)]
    Class(String),
    #[regex(r#""[^"]*""#,
        |lex| lex.slice()[1..lex.slice().len()-1].to_string(), priority = 1)]
    TextLiteral(String),
    #[regex(r"[a-zA-Z_][a-zA-Z0-9_-]*",
        |lex| lex.slice().to_string(), priority = 1)]
    Ident(String),
    #[regex(r"[ \t]+", |lex| lex.slice().to_string())]
    Whitespace(String),
    #[regex(r".", priority = 0)]
    Unknown,
}
