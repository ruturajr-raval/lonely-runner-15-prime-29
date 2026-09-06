use std::env;
use std::process::ExitCode;

const COORDINATES: usize = 14;
const CHOICES: usize = 15;
const PRIME: i32 = 29;
const LEVEL: i32 = 15;
const MODULUS: i32 = PRIME * LEVEL;
const TIMES: usize = (MODULUS / 2) as usize;
const ALL_CHOICES: u16 = (1_u16 << CHOICES) - 1;
const VERSION: &str = "1.0.0";

#[derive(Clone, Copy, Eq, PartialEq)]
enum SymmetryCase {
    Coprime,
    Noncoprime,
}

struct Solver {
    symmetry_case: SymmetryCase,
    require_gcd_failure: bool,
    fixed_choices: Vec<(usize, usize)>,
    bad_masks: [[u16; COORDINATES]; TIMES],
    nondivisible_by_three: u16,
    nondivisible_by_five: u16,
    noncoprime: u16,
    solution: [usize; COORDINATES],
    nodes: u64,
    propagations: u64,
    domain_branches: u64,
    internal_error: bool,
}

impl Solver {
    fn new(
        symmetry_case: SymmetryCase,
        require_gcd_failure: bool,
        fixed_choices: Vec<(usize, usize)>,
    ) -> Self {
        let mut solver = Self {
            symmetry_case,
            require_gcd_failure,
            fixed_choices,
            bad_masks: [[0; COORDINATES]; TIMES],
            nondivisible_by_three: 0,
            nondivisible_by_five: 0,
            noncoprime: 0,
            solution: [0; COORDINATES],
            nodes: 0,
            propagations: 0,
            domain_branches: 0,
            internal_error: false,
        };
        solver.build_masks();
        solver
    }

    fn build_masks(&mut self) {
        for time in 1..=TIMES {
            for coordinate in 1..=COORDINATES {
                let mut mask = 0_u16;
                for residue in 0..CHOICES {
                    if bad_by_crt(time as i32, coordinate as i32, residue as i32)
                    {
                        mask |= 1_u16 << residue;
                    }
                }
                self.bad_masks[time - 1][coordinate - 1] = mask;
            }
        }

        for residue in 0..CHOICES {
            if residue % 3 != 0 {
                self.nondivisible_by_three |= 1_u16 << residue;
            }
            if residue % 5 != 0 {
                self.nondivisible_by_five |= 1_u16 << residue;
            }
            if residue % 3 == 0 || residue % 5 == 0 {
                self.noncoprime |= 1_u16 << residue;
            }
        }
    }

    fn solve(&mut self) -> bool {
        let mut domains = [ALL_CHOICES; COORDINATES];
        match self.symmetry_case {
            SymmetryCase::Coprime => domains[0] = 1_u16 << 1,
            SymmetryCase::Noncoprime => {
                for domain in &mut domains {
                    *domain &= self.noncoprime;
                }
                domains[2] = 1_u16 << 3;
            }
        }

        for &(coordinate, lift_choice) in &self.fixed_choices {
            let residue = residue_from_lift_choice(coordinate, lift_choice);
            domains[coordinate] &= 1_u16 << residue;
            if domains[coordinate] == 0 {
                return false;
            }
        }
        self.search(domains)
    }

    fn propagate_cardinality(&self, domains: &mut [u16; COORDINATES], mask: u16) -> bool {
        let mut guaranteed = 0_usize;
        let mut optional = Vec::new();
        for (coordinate, domain) in domains.iter().copied().enumerate() {
            let qualifying = domain & mask;
            if qualifying == 0 {
                continue;
            }
            if qualifying == domain {
                guaranteed += 1;
            } else {
                optional.push(coordinate);
            }
        }
        if guaranteed >= 2 {
            return true;
        }
        if guaranteed + optional.len() < 2 {
            return false;
        }
        if guaranteed + optional.len() == 2 {
            for coordinate in optional {
                domains[coordinate] &= mask;
                if domains[coordinate] == 0 {
                    return false;
                }
            }
        }
        true
    }

    fn propagate(&mut self, domains: &mut [u16; COORDINATES]) -> bool {
        loop {
            self.propagations += 1;
            let before = *domains;
            if self.require_gcd_failure
                && (!self.propagate_cardinality(
                    domains,
                    self.nondivisible_by_three,
                ) || !self.propagate_cardinality(
                    domains,
                    self.nondivisible_by_five,
                ))
            {
                return false;
            }

            for time in 0..TIMES {
                let mut guaranteed = false;
                let mut candidate_coordinate = 0_usize;
                let mut candidate_coordinates = 0_usize;
                for (coordinate, domain) in domains.iter().copied().enumerate() {
                    let covering = domain & self.bad_masks[time][coordinate];
                    if covering == domain {
                        guaranteed = true;
                        break;
                    }
                    if covering != 0 {
                        candidate_coordinate = coordinate;
                        candidate_coordinates += 1;
                    }
                }
                if guaranteed {
                    continue;
                }
                if candidate_coordinates == 0 {
                    return false;
                }
                if candidate_coordinates == 1 {
                    domains[candidate_coordinate] &=
                        self.bad_masks[time][candidate_coordinate];
                    if domains[candidate_coordinate] == 0 {
                        return false;
                    }
                }
            }
            if *domains == before {
                return true;
            }
        }
    }

    fn all_constraints_guaranteed(&self, domains: &[u16; COORDINATES]) -> bool {
        for time in 0..TIMES {
            if !domains.iter().copied().enumerate().any(|(coordinate, domain)| {
                domain & self.bad_masks[time][coordinate] == domain
            }) {
                return false;
            }
        }
        if self.require_gcd_failure {
            for mask in [
                self.nondivisible_by_three,
                self.nondivisible_by_five,
            ] {
                let guaranteed = domains
                    .iter()
                    .copied()
                    .filter(|domain| domain & mask == *domain)
                    .count();
                if guaranteed < 2 {
                    return false;
                }
            }
        }
        true
    }

    fn validate_solution(&self) -> bool {
        if self.require_gcd_failure {
            let nondivisible_by_three = self
                .solution
                .iter()
                .filter(|&&residue| residue % 3 != 0)
                .count();
            let nondivisible_by_five = self
                .solution
                .iter()
                .filter(|&&residue| residue % 5 != 0)
                .count();
            if nondivisible_by_three < 2 || nondivisible_by_five < 2 {
                return false;
            }
        }
        for time in 0..TIMES {
            if !(0..COORDINATES).any(|coordinate| {
                let residue = self.solution[coordinate];
                self.bad_masks[time][coordinate] & (1_u16 << residue) != 0
            }) {
                return false;
            }
        }
        true
    }

    fn record_solution(&mut self, domains: &[u16; COORDINATES]) -> bool {
        for (coordinate, domain) in domains.iter().copied().enumerate() {
            self.solution[coordinate] = domain.trailing_zeros() as usize;
        }
        self.validate_solution()
    }

    fn select_branch_time(
        &self,
        domains: &[u16; COORDINATES],
    ) -> Option<Vec<(usize, usize)>> {
        let mut best: Option<(usize, usize, Vec<(usize, usize)>)> = None;
        for time in 0..TIMES {
            let mut guaranteed = false;
            let mut coordinates = 0_usize;
            let mut literals = Vec::new();
            for (coordinate, domain) in domains.iter().copied().enumerate() {
                let covering = domain & self.bad_masks[time][coordinate];
                if covering == domain {
                    guaranteed = true;
                    break;
                }
                if covering != 0 {
                    coordinates += 1;
                    let mut choices = covering;
                    while choices != 0 {
                        let residue = choices.trailing_zeros() as usize;
                        literals.push((coordinate, residue));
                        choices &= choices - 1;
                    }
                }
            }
            if guaranteed {
                continue;
            }
            let score = (literals.len(), coordinates);
            if best
                .as_ref()
                .is_none_or(|current| score < (current.0, current.1))
            {
                best = Some((score.0, score.1, literals));
            }
        }
        best.map(|(_, _, literals)| literals)
    }

    fn search(&mut self, mut domains: [u16; COORDINATES]) -> bool {
        if self.internal_error {
            return false;
        }
        self.nodes += 1;
        if self.nodes.is_multiple_of(1_000_000) {
            eprintln!("nodes {}", self.nodes);
        }
        if !self.propagate(&mut domains) {
            return false;
        }
        if self.all_constraints_guaranteed(&domains) {
            let valid = self.record_solution(&domains);
            if !valid {
                self.internal_error = true;
            }
            return valid;
        }

        if let Some(literals) = self.select_branch_time(&domains) {
            let mut remaining = domains;
            for (coordinate, residue) in literals {
                let bit = 1_u16 << residue;
                if remaining[coordinate] & bit == 0 {
                    continue;
                }
                let mut branch = remaining;
                branch[coordinate] = bit;
                if self.search(branch) {
                    return true;
                }
                if self.internal_error {
                    return false;
                }
                remaining[coordinate] &= !bit;
                if remaining[coordinate] == 0 {
                    break;
                }
            }
            return false;
        }

        let branch_coordinate = domains
            .iter()
            .copied()
            .enumerate()
            .filter(|(_, domain)| domain.count_ones() > 1)
            .min_by_key(|(_, domain)| domain.count_ones())
            .map(|(coordinate, _)| coordinate);
        let Some(coordinate) = branch_coordinate else {
            self.internal_error = true;
            return false;
        };
        self.domain_branches += 1;
        let mut choices = domains[coordinate];
        while choices != 0 {
            let residue = choices.trailing_zeros() as usize;
            let mut branch = domains;
            branch[coordinate] = 1_u16 << residue;
            if self.search(branch) {
                return true;
            }
            if self.internal_error {
                return false;
            }
            choices &= choices - 1;
        }
        false
    }

    fn print_result(&self, satisfiable: bool) {
        let case = match self.symmetry_case {
            SymmetryCase::Coprime => "coprime",
            SymmetryCase::Noncoprime => "noncoprime",
        };
        println!("case {case}");
        println!(
            "constraint_mode {}",
            if self.require_gcd_failure {
                "improperness"
            } else {
                "time-cover-only"
            }
        );
        println!(
            "status {}",
            if self.internal_error {
                "ERROR"
            } else if satisfiable {
                "SAT"
            } else {
                "UNSAT"
            }
        );
        println!("nodes {}", self.nodes);
        println!("propagations {}", self.propagations);
        println!("domain_branches {}", self.domain_branches);
        for &(coordinate, lift_choice) in &self.fixed_choices {
            println!("fixed {}:{lift_choice}", coordinate + 1);
        }
        if satisfiable {
            print!("residues");
            for residue in self.solution {
                print!(" {residue}");
            }
            println!();
            print!("speeds");
            for (coordinate, residue) in self.solution.iter().copied().enumerate()
            {
                print!(" {}", speed_from_residue(coordinate, residue));
            }
            println!();
        }
    }
}

fn bad_by_crt(time: i32, coordinate: i32, residue: i32) -> bool {
    let time_mod_prime = time.rem_euclid(PRIME);
    let time_mod_level = time.rem_euclid(LEVEL);
    let product_mod_prime = (time_mod_prime * coordinate).rem_euclid(PRIME);
    let product_mod_level = (time_mod_level * residue).rem_euclid(LEVEL);
    if product_mod_prime == 0 {
        product_mod_level == 0
    } else {
        product_mod_level == product_mod_prime.rem_euclid(LEVEL)
            || product_mod_level
                == (product_mod_prime + 1).rem_euclid(LEVEL)
    }
}

fn residue_from_lift_choice(coordinate: usize, lift_choice: usize) -> usize {
    ((coordinate + 1 + LEVEL as usize) - lift_choice) % LEVEL as usize
}

fn speed_from_residue(coordinate: usize, residue: usize) -> i32 {
    let one_based = coordinate as i32 + 1;
    let lift_choice = (one_based - residue as i32).rem_euclid(LEVEL);
    one_based + PRIME * lift_choice
}

fn bad_direct(time: i32, coordinate: usize, residue: usize) -> bool {
    let value = speed_from_residue(coordinate, residue);
    let product = (time * value).rem_euclid(MODULUS);
    let distance = product.min(MODULUS - product);
    LEVEL * distance < MODULUS
}

fn self_test() -> bool {
    for time in 1..=TIMES {
        for coordinate in 0..COORDINATES {
            let mut seen = [false; CHOICES];
            for lift_choice in 0..CHOICES {
                let residue =
                    residue_from_lift_choice(coordinate, lift_choice);
                seen[residue] = true;
                if bad_by_crt(
                    time as i32,
                    coordinate as i32 + 1,
                    residue as i32,
                ) != bad_direct(time as i32, coordinate, residue)
                {
                    return false;
                }
            }
            if seen.iter().any(|value| !value) {
                return false;
            }
        }
    }
    true
}

fn parse_fixed(value: &str) -> Result<(usize, usize), String> {
    let Some((coordinate_text, choice_text)) = value.split_once(':') else {
        return Err(format!("invalid fixed choice: {value}"));
    };
    if choice_text.contains(':') {
        return Err(format!("invalid fixed choice: {value}"));
    }
    let coordinate = coordinate_text
        .parse::<usize>()
        .map_err(|_| format!("invalid fixed choice: {value}"))?;
    let choice = choice_text
        .parse::<usize>()
        .map_err(|_| format!("invalid fixed choice: {value}"))?;
    if !(1..=COORDINATES).contains(&coordinate) || choice >= CHOICES {
        return Err(format!("invalid fixed choice: {value}"));
    }
    Ok((coordinate - 1, choice))
}

fn run() -> Result<i32, String> {
    let arguments: Vec<String> = env::args().skip(1).collect();
    if arguments == ["--version"] {
        println!("verify_p29_level15 {VERSION}");
        println!("rustc {}", option_env!("RUSTC_VERSION").unwrap_or("unknown"));
        return Ok(0);
    }
    if arguments == ["--self-test"] {
        let passed = self_test();
        println!("self_test {}", if passed { "PASS" } else { "FAIL" });
        return Ok(if passed { 0 } else { 1 });
    }
    let Some(requested_case) = arguments.first() else {
        return Err(
            "usage: verify_p29_level15 \
             coprime|noncoprime|coprime-cover \
             [COORDINATE:CHOICE ...]"
                .to_string(),
        );
    };
    let (symmetry_case, require_gcd_failure) = match requested_case.as_str() {
        "coprime" => (SymmetryCase::Coprime, true),
        "noncoprime" => (SymmetryCase::Noncoprime, true),
        "coprime-cover" => (SymmetryCase::Coprime, false),
        _ => return Err(format!("unknown symmetry case: {requested_case}")),
    };

    let mut fixed_by_coordinate = [None; COORDINATES];
    let mut fixed_choices = Vec::new();
    for value in &arguments[1..] {
        let (coordinate, choice) = parse_fixed(value)?;
        if fixed_by_coordinate[coordinate].is_some() {
            return Err(format!(
                "duplicate fixed coordinate: {}",
                coordinate + 1
            ));
        }
        fixed_by_coordinate[coordinate] = Some(choice);
        fixed_choices.push((coordinate, choice));
    }

    let mut solver = Solver::new(
        symmetry_case,
        require_gcd_failure,
        fixed_choices,
    );
    let satisfiable = solver.solve();
    solver.print_result(satisfiable);
    if solver.internal_error {
        Ok(2)
    } else if satisfiable {
        Ok(10)
    } else {
        Ok(20)
    }
}

fn main() -> ExitCode {
    match run() {
        Ok(code) => ExitCode::from(code as u8),
        Err(message) => {
            eprintln!("{message}");
            ExitCode::from(2)
        }
    }
}
