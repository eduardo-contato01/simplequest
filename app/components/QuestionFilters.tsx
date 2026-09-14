export type QuestionFiltersProps = {
  query: string; school: string; year: string; subject: string; status: string;
  schools: string[]; years: number[]; subjects: string[];
  setQuery: (value: string) => void; setSchool: (value: string) => void;
  setYear: (value: string) => void; setSubject: (value: string) => void;
  setStatus: (value: string) => void; setPage: (value: number) => void;
  clearFilters: () => void;
};

export function QuestionFilters({ query, school, year, subject, status, schools, years, subjects, setQuery, setSchool, setYear, setSubject, setStatus, setPage, clearFilters }: QuestionFiltersProps) {
  return (
    <div className="search-panel">
      <div className="search-row">
        <label className="search-box">
          <span aria-hidden="true">⌕</span>
          <input
            value={query}
            onChange={(event) => { setQuery(event.target.value); setPage(1); }}
            placeholder="Busque por palavra, assunto ou número da questão"
            aria-label="Pesquisar questões"
          />
          <kbd>Ctrl K</kbd>
        </label>
        <button className="primary-button" onClick={() => setPage(1)}>Pesquisar</button>
      </div>
      <div className="filters" aria-label="Filtros da pesquisa">
        <label><span>Prova</span><select value={school} onChange={(e) => { setSchool(e.target.value); setPage(1); }}><option value="">Todas</option>{schools.map((item) => <option key={item}>{item}</option>)}</select></label>
        <label><span>Ano</span><select value={year} onChange={(e) => { setYear(e.target.value); setPage(1); }}><option value="">Todos</option>{years.map((item) => <option key={item}>{item}</option>)}</select></label>
        <label className="subject-filter"><span>Assunto</span><select value={subject} onChange={(e) => { setSubject(e.target.value); setPage(1); }}><option value="">Todos os assuntos</option>{subjects.map((item) => <option key={item}>{item}</option>)}</select></label>
        <label><span>Conteúdo</span><select value={status} onChange={(e) => { setStatus(e.target.value); setPage(1); }}><option value="">Todos</option><option value="authenticated">Autenticadas</option><option value="ready">Texto importado</option><option value="review">Em revisão</option></select></label>
        <button className="clear-button" onClick={clearFilters}>Limpar filtros</button>
      </div>
    </div>
  );
}
