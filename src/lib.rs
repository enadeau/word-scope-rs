use pyo3::prelude::*;
use pyo3::basic::CompareOp;
use pyo3::exceptions::PyIndexError;
// use pyo3::types::PySlice;

use std::collections::hash_map::DefaultHasher;

// Required to call the `.hash` and `.finish` methods, which are defined on traits.
use std::hash::{Hash, Hasher};


#[pyclass(sequence)]
struct Word {
    letters: Vec<char>
}

#[pymethods]
impl Word {
    #[new]
    fn py_new(word: Option<String>) -> Self {
        let letters = match word {
            None => vec![],
            Some(w) => w.chars().collect()
        };
        Word {letters}
    }

    fn __iter__(slf: PyRef<'_, Self>) -> PyResult<Py<WordIterator>> {
        let iter = WordIterator {inner: slf.letters.clone().into_iter()};
        Py::new(slf.py(), iter)
    }

    fn __str__(&self) -> String {
        self.letters.iter().cloned().collect::<String>()
    }

    fn __len__(&self) -> usize {
        self.letters.len()
    }

    fn __add__(slf: PyRef<'_, Self>, object: String) -> Word {
        let letters = slf.letters.clone().into_iter().chain(object.chars()).collect();
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

/// A Python module implemented in Rust.
#[pymodule]
fn word_scope_rs(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<Word>()?;
    Ok(())
}
