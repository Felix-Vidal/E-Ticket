package br.ufac.eticketapi.repository;

import org.springframework.data.jpa.repository.JpaRepository;

import br.ufac.eticketapi.model.TicketUnico;

public interface TicketUnicoRepository extends JpaRepository<TicketUnico, Long>{
    
}
