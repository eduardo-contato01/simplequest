export type QuestionsPaginationProps = { currentPage: number; pageCount: number; setPage: (page: number) => void };

export function QuestionsPagination({ currentPage, pageCount, setPage }: QuestionsPaginationProps) {
  if (pageCount <= 1) return null;
  return (
    <nav className="pagination" aria-label="Paginação das questões">
      <button disabled={currentPage === 1} onClick={() => setPage(currentPage - 1)}>Anterior</button>
      <span>Página <strong>{currentPage}</strong> de {pageCount}</span>
      <button disabled={currentPage === pageCount} onClick={() => setPage(currentPage + 1)}>Próxima</button>
    </nav>
  );
}
