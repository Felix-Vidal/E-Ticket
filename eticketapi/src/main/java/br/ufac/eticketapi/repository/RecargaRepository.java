package br.ufac.eticketapi.repository;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import br.ufac.eticketapi.model.Recarga;

public interface RecargaRepository extends JpaRepository<Recarga, Long>{

    @Query("SELECT r FROM Recarga r" +
        " LEFT JOIN Usuario u ON u.id = r.usuario.id" +
        " WHERE u.id = %?1%"
    )
    List<Recarga> findByUsuarioId(Long id);

}
