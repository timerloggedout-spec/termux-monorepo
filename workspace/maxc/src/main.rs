use logos::Logos;
mod emitter;
mod emitter_leptos;
mod emitter_micro;
mod lexer;
mod reverse;
mod parser;

use std::env;
use std::fs;
use std::io::{self, Read};
use base64::Engine;

fn main() {
    let args: Vec<String> = env::args().collect();
    let mut show_tokens = false;
    let mut show_ast = false;
    let mut target = "html";
    let mut output_file: Option<String> = None;
    let mut input_file: Option<String> = None;
    let mut memelord = false;

    let mut i = 1;
    while i < args.len() {
        match args[i].as_str() {
            "--tokens" => show_tokens = true,
            "--ast" => show_ast = true,
            "--output-mutml" => {
                memelord = true;
                output_file = Some("output.mutml".to_string());
            }
            "-t" => {
                i += 1;
                if i < args.len() {
                    target = &args[i];
                } else {
                    eprintln!("maxc: -t requires a backend name");
                    std::process::exit(1);
                }
            }
            "-o" => {
                i += 1;
                if i < args.len() {
                    output_file = Some(args[i].clone());
                } else {
                    eprintln!("maxc: -o requires a filename");
                    std::process::exit(1);
                }
            }
            "--help" | "-h" => {
                println!("maxc — MaxUp Compiler v0.1.0\n");
                println!("Usage: maxc [flags] [input.max] [-o output.mu] [-t <backend>]\n");
                println!("Backends:");
                println!("  html  (default)  Standard HTML5 output");
                println!("  leptos            Leptos RSX (WASM) output");
                println!("Flags:");
                println!("  --tokens    Print token stream only (debug)");
                println!("  --ast       Print AST only (debug)");
                println!("  -o <file>   Write output to file");
                println!("  --help, -h  Show this help");
                return;
            }
            arg if !arg.starts_with('-') => input_file = Some(arg.to_string()),
            _ => {
                eprintln!("maxc: unknown flag: {}", args[i]);
                std::process::exit(1);
            }
        }
        i += 1;
    }

    // Read source
    let source = if let Some(path) = &input_file {
        if path == "-" {
            let mut buf = String::new();
            io::stdin().read_to_string(&mut buf).unwrap_or_else(|e| {
                eprintln!("maxc: reading stdin: {}", e);
                std::process::exit(1);
            });
            buf
        } else {
            fs::read_to_string(path).unwrap_or_else(|e| {
                eprintln!("maxc: cannot read '{}': {}", path, e);
                std::process::exit(1);
            })
        }
    } else {
        "; .container\n  p {{ title }}\n  + on:click=\"increment\" \"Click me\"\n".to_string()
    };

    let lex = lexer::Token::lexer(&source);
    let tokens: Vec<lexer::Token> = lex.filter_map(|r| r.ok()).collect();

    if show_tokens || show_ast {
        if show_tokens {
            println!("{:?}", tokens);
        }
        if show_ast {
            let ast = parser::parse(&tokens);
            println!("{:#?}", ast);
        }
        return;
    }

    let ast = parser::parse(&tokens);
    let output = match target {
        "leptos" => ast
            .iter()
            .map(emitter_leptos::emit_leptos)
            .collect::<Vec<_>>()
            .join("\n"),
        "micro" => {
            let bytes = emitter_micro::emit_micro(&ast);
            if let Some(path) = &output_file {
                std::fs::write(path, &bytes).unwrap_or_else(|e| {
                    eprintln!("maxc: cannot write '{}': {}", path, e);
                    std::process::exit(1);
                });
                return;
            } else {
                println!("{}", base64::engine::general_purpose::STANDARD.encode(&bytes));
                return;
            }
        }
        _ => ast
            .iter()
            .map(emitter::emit_html)
            .collect::<Vec<_>>()
            .join("\n"),
    };
    let final_output = if memelord {
        eprintln!("🦊 Memelords activated! .mutml supremacy!");
        format!(
            "<!-- MUTML: This file was compiled with MAXC --!>\n{}",
            output
        )
    } else {
        output
    };

    if let Some(path) = &output_file {
        fs::write(path, &final_output).unwrap_or_else(|e| {
            eprintln!("maxc: cannot write '{}': {}", path, e);
            std::process::exit(1);
        });
    } else {
        println!("{}", final_output);
    }
}
