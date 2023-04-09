use pyo3::basic::CompareOp;
use pyo3::exceptions::{PyIndexError, PyNotImplementedError};
use pyo3::prelude::*;
use std::cmp;
// use pyo3::types::PySlice;

use std::collections::hash_map::DefaultHasher;

// Required to call the `.hash` and `.finish` methods, which are defined on traits.
use std::hash::{Hash, Hasher};

#[pyclass(sequence)]
struct Word {
    letters: Vec<char>,
}

#[pymethods]
impl Word {
    #[new]
    fn py_new(word: Option<String>) -> Self {
        let letters = match word {
            None => vec![],
            Some(w) => w.chars().collect(),
        };
        Word { letters }
    }

    fn __iter__(slf: PyRef<'_, Self>) -> PyResult<Py<WordIterator>> {
        let iter = WordIterator {
            inner: slf.letters.clone().into_iter(),
        };
        Py::new(slf.py(), iter)
    }

    fn __str__(&self) -> String {
        self.letters.iter().cloned().collect::<String>()
    }

    fn __len__(&self) -> usize {
        self.letters.len()
    }

    fn __add__(slf: PyRef<'_, Self>, object: String) -> Word {
        let letters = slf
            .letters
            .clone()
            .into_iter()
            .chain(object.chars())
            .collect();
        Word { letters }
    }

    fn __richcmp__(&self, other: &Self, op: CompareOp) -> bool {
        op.matches(self.letters.cmp(&other.letters))
    }

    fn __hash__(&self) -> u64 {
        let mut hasher = DefaultHasher::new();
        self.letters.hash(&mut hasher);
        hasher.finish()
    }

    fn __getitem__(&self, index: isize) -> PyResult<char> {
        let mut corrected_index = index;
        if index < 0 {
            corrected_index = index + isize::try_from(self.letters.len()).expect("Index to big");
        }
        println!("{corrected_index} {:?}", self.letters);
        let corrected_index: usize = usize::try_from(corrected_index).expect("Invalid index");
        match self.letters.get(corrected_index) {
            None => Err(PyIndexError::new_err("Index out of range")),
            Some(c) => Ok(*c),
        }
    }
}

impl Word {
    fn contains(&self, pattern: &Self) -> bool {
        let word_str: String = self.letters.iter().collect();
        let pattern_str: String = pattern.letters.iter().collect();
        word_str.contains(&pattern_str)
    }
}

#[pyclass]
struct WordIterator {
    inner: std::vec::IntoIter<char>,
}

#[pymethods]
impl WordIterator {
    fn __iter__(slf: PyRef<'_, Self>) -> PyRef<'_, Self> {
        slf
    }

    fn __next__(mut slf: PyRefMut<'_, Self>) -> Option<char> {
        slf.inner.next()
    }
}

#[pyclass]
#[derive(PartialEq, Eq, Hash)]
struct AvoidingWithPrefix {
    #[pyo3(get)]
    prefix: String,
    #[pyo3(get)]
    patterns: Vec<String>,
    #[pyo3(get)]
    alphabet: Vec<char>,
    #[pyo3(get, name = "just_prefix")]
    is_just_prefix: bool,
}

#[pymethods]
impl AvoidingWithPrefix {
    #[new]
    #[pyo3(signature=(prefix, patterns,alphabet,just_prefix=false))]
    fn py_new(
        prefix: String,
        patterns: Vec<String>,
        alphabet: Vec<char>,
        just_prefix: bool,
    ) -> AvoidingWithPrefix {
        AvoidingWithPrefix {
            prefix,
            patterns,
            alphabet,
            is_just_prefix: just_prefix,
        }
    }

    fn is_empty(&self) -> bool {
        self.patterns.iter().any(|patt| self.prefix.contains(patt))
    }

    fn is_atom(&self) -> bool {
        self.is_just_prefix
    }

    fn removable_prefix_length(&self) -> usize {
        let m = self.patterns.iter().map(|s| s.len()).max().unwrap_or(1);
        let mut safe = if self.prefix.len() > m {
            self.prefix.len() - m + 0
        } else {
            0
        };
        for i in safe..self.prefix.len() {
            let end = &self.prefix[i..];
            if self
                .patterns
                .iter()
                .any(|patt| end == &patt[..cmp::min(end.len(), patt.len())])
            {
                break;
            }
            safe = i + 1;
        }
        safe
    }

    fn minimum_size_of_object(&self) -> usize {
        self.prefix.len()
    }

    fn __hash__(&self) -> u64 {
        let mut hasher = DefaultHasher::new();
        self.hash(&mut hasher);
        hasher.finish()
    }

    fn __richcmp__(&self, other: &Self, op: CompareOp, py: Python<'_>) -> PyObject {
        match op {
            CompareOp::Eq => (self == other).into_py(py),
            CompareOp::Ne => (self != other).into_py(py),
            _ => py.NotImplemented(),
        }
    }

    fn to_bytes(&self) -> PyResult<Vec<u8>> {
        Err(PyNotImplementedError::new_err("to bytes not implemented"))
    }
}

/// A Python module implemented in Rust.
#[pymodule]
fn word_scope_rs(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<Word>()?;
    m.add_class::<AvoidingWithPrefix>()?;
    Ok(())
}
