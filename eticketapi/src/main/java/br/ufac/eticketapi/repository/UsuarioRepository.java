package br.ufac.eticketapi.repository;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import br.ufac.eticketapi.model.Usuario;

public interface UsuarioRepository extends JpaRepository<Usuario, Long>{

    @Query(
        "SELECT u FROM Usuario u" +
        " LEFT JOIN Classificacao c" +
        " WHERE u.nomeCompleto LIKE %?1%" +
        " OR u.nomeSocial LIKE %?1%" +
        " OR u.matricula LIKE %?1%" +
        " OR c.nome LIKE %?1%" + 
        " OR u.cpf LIKE %?1%" +
        " OR u.unidade LIKE %?1%"
    )
    
    List<Usuario> findByAll(String termoBusca);

}
