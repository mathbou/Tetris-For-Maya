// Copyright (c) 2025 Mathieu Bouzard.
//
// This file is part of Tetris For Maya
// (see https://gitlab.com/mathbou/TetrisMaya).
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program. If not, see <http://www.gnu.org/licenses/>.

/// https://github.com/Jij-Inc/pyo3-stub-gen/issues/161

use proc_macro::TokenStream;
use quote::quote;
use syn::{Item, parse_macro_input};

#[proc_macro_attribute]
pub fn stubgen(_attrs: TokenStream, item: TokenStream) -> TokenStream {
    let input = parse_macro_input!(item as Item);

    // Wrap the item with #[cfg_attr(feature = "stubgen", ...)]
    let output = match input {
        Item::Enum(e) => {
            quote! {
                #[cfg_attr(feature = "stubgen", pyo3_stub_gen::derive::gen_stub_pyclass_enum)]
                #e
            }
        }
        Item::Struct(s) => {
            quote! {
                #[cfg_attr(feature = "stubgen", pyo3_stub_gen::derive::gen_stub_pyclass)]
                #s
            }
        }
        Item::Impl(i) => {
            quote! {
                #[cfg_attr(feature = "stubgen", pyo3_stub_gen::derive::gen_stub_pymethods)]
                #i
            }
        }
        Item::Fn(f) => {
            quote! {
                #[cfg_attr(feature = "stubgen", pyo3_stub_gen::derive::gen_stub_pyfunction)]
                #f
            }
        }
        _ => {
            quote! {
                #input
            }
        }
    };

    output.into()
}
