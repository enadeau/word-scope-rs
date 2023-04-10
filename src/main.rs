use word_scope_rs::AvoidingWithPrefix;

fn main() {
    let prefix = String::from("ab");
    let alphabet = vec!['a', 'b'];
    let patterns = vec![String::from("aaab")];
    let c = AvoidingWithPrefix::new(prefix, patterns, alphabet, false);
    for n in 0..10 {
        let count = c.objects_of_size(n).count();
        println!("{n}: {count}");
    }
}
