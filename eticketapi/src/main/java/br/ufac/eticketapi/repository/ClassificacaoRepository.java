package br.ufac.eticketapi.repository;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import br.ufac.eticketapi.model.Classificacao;

public interface ClassificacaoRepository extends JpaRepository<Classificacao, Long>{

    @Query(
        "SELECT c FROM Classificacao c WHERE c.nome LIKE %?1%"
    )   
    List<Classificacao> findByAll(String termoBusca);

}
